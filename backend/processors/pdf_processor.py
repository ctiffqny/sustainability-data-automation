from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

import pdfplumber

from backend.core.pdf_config_utils import (
    PDFConfigError,
    PDFConfigLoader,
)

class PDFProcessingError(Exception):
    """Raised when a food-waste PDF cannot be processed."""


class PDFLocationNotFoundError(PDFProcessingError):
    """Raised when the collection point cannot be identified."""


class PDFLocationAmbiguousError(PDFProcessingError):
    """Raised when a PDF appears to match multiple locations."""


class PDFRecordNotFoundError(PDFProcessingError):
    """Raised when a requested month cannot be found."""


class PDFProcessor:
    MONTH_REGEX = re.compile(
        r"\b"
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\s*[-–—/]\s*"
        r"(\d{2}|\d{4})"
        r"\b",
        re.IGNORECASE,
    )

    def __init__(
        self,
        config_path: str | Path | None = None,
    ) -> None:
        self.config_loader = PDFConfigLoader(
            config_path
        )

    def extract_record(
        self,
        pdf_path: str | Path,
        *,
        month: str,
        location_key: str | None = None,
    ) -> dict[str, Any]:
        """Extract one populated monthly record from a food-waste PDF."""
        path = self._validate_pdf_path(pdf_path)
        normalized_month = self.normalize_month(month)

        try:
            with pdfplumber.open(path) as pdf:
                if not pdf.pages:
                    raise PDFProcessingError(
                        f"The PDF contains no pages: {path.name}"
                    )

                document_text = self._extract_document_text(pdf.pages)

                resolved_key, location_config = self._resolve_location(
                    document_text=document_text,
                    requested_location_key=location_key,
                )

                records = self._extract_all_records(
                    pages=pdf.pages,
                    path=path,
                    location_key=resolved_key,
                    location_config=location_config,
                )

                for record in records:
                    if record["month"] == normalized_month:
                        return record

        except (PDFProcessingError, PDFConfigError):
            raise
        except Exception as exc:
            raise PDFProcessingError(
                f"Could not process PDF '{path.name}': {exc}"
            ) from exc

        raise PDFRecordNotFoundError(
            f"No populated record was found for {normalized_month} "
            f"in '{path.name}'."
        )

    def extract_total_amount(
        self,
        pdf_path: str | Path,
        *,
        month: str,
        location_key: str | None = None,
    ) -> Decimal:
        """Extract only the monthly total amount in tonnes."""
        record = self.extract_record(
            pdf_path,
            month=month,
            location_key=location_key,
        )

        total = record["total_amount_tonnes"]

        if total is None:
            raise PDFRecordNotFoundError(
                f"The total amount for {record['location']}, "
                f"{record['month']} is blank."
            )

        return Decimal(str(total))

    def extract_all_months(
        self,
        pdf_path: str | Path,
        *,
        location_key: str | None = None,
    ) -> list[dict[str, Any]]:
        """Extract every populated monthly row from one PDF."""
        path = self._validate_pdf_path(pdf_path)

        try:
            with pdfplumber.open(path) as pdf:
                if not pdf.pages:
                    raise PDFProcessingError(
                        f"The PDF contains no pages: {path.name}"
                    )

                document_text = self._extract_document_text(pdf.pages)

                resolved_key, location_config = self._resolve_location(
                    document_text=document_text,
                    requested_location_key=location_key,
                )

                records = self._extract_all_records(
                    pages=pdf.pages,
                    path=path,
                    location_key=resolved_key,
                    location_config=location_config,
                )

                return self._deduplicate_records(records)

        except PDFProcessingError:
            raise
        except Exception as exc:
            raise PDFProcessingError(
                f"Could not process PDF '{path.name}': {exc}"
            ) from exc

    def identify_location(
        self,
        pdf_path: str | Path,
    ) -> dict[str, str]:
        """Return the detected location key and display name."""
        path = self._validate_pdf_path(pdf_path)

        try:
            with pdfplumber.open(path) as pdf:
                document_text = self._extract_document_text(pdf.pages)

                location_key, config = self._resolve_location(
                    document_text=document_text,
                    requested_location_key=None,
                )

                return {
                    "location_key": location_key,
                    "location": str(config["display_name"]),
                }

        except PDFProcessingError:
            raise
        except Exception as exc:
            raise PDFProcessingError(
                f"Could not identify location in '{path.name}': {exc}"
            ) from exc

    def _extract_all_records(
        self,
        *,
        pages: Iterable[Any],
        path: Path,
        location_key: str,
        location_config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []

        for page_number, page in enumerate(pages, start=1):
            records.extend(
                self._extract_all_from_page(
                    page=page,
                    path=path,
                    location_key=location_key,
                    location_config=location_config,
                    page_number=page_number,
                )
            )

        return records

    def _extract_all_from_page(
        self,
        *,
        page: Any,
        path: Path,
        location_key: str,
        location_config: dict[str, Any],
        page_number: int,
    ) -> list[dict[str, Any]]:
        parser_type = location_config.get(
            "parser_type",
            "bordered_table",
        )

        if parser_type != "bordered_table":
            raise PDFProcessingError(
                f"Unsupported parser type '{parser_type}' "
                f"for location '{location_key}'."
            )

        table_settings = location_config.get(
            "table_settings",
            {},
        )

        tables = page.extract_tables(
            table_settings=table_settings,
        )

        records: list[dict[str, Any]] = []

        for table in tables:
            records.extend(
                self._records_from_table(
                    table=table,
                    path=path,
                    location_key=location_key,
                    location_config=location_config,
                    page_number=page_number,
                )
            )

        return records

    def _records_from_table(
        self,
        *,
        table: list[list[Any] | None],
        path: Path,
        location_key: str,
        location_config: dict[str, Any],
        page_number: int,
    ) -> list[dict[str, Any]]:
        column_map = location_config.get("columns", {})

        month_index = self._require_column_index(
            column_map,
            "month",
        )
        collection_days_index = self._require_column_index(
            column_map,
            "collection_days",
        )
        daily_average_index = self._require_column_index(
            column_map,
            "daily_average",
        )
        total_amount_index = self._require_column_index(
            column_map,
            "total_amount",
        )

        records: list[dict[str, Any]] = []

        for raw_row in table:
            if raw_row is None:
                continue

            row = [
                self._clean_cell(cell)
                for cell in raw_row
            ]

            month_cell = self._get_cell(row, month_index)
            normalized_month = self.normalize_month(
                month_cell,
                strict=False,
            )

            if normalized_month is None:
                continue

            collection_days = self._parse_integer(
                self._get_cell(row, collection_days_index)
            )
            daily_average = self._parse_decimal(
                self._get_cell(row, daily_average_index)
            )
            total_amount = self._parse_decimal(
                self._get_cell(row, total_amount_index)
            )

            # Ignore empty future-month rows.
            if (
                collection_days is None
                and daily_average is None
                and total_amount is None
            ):
                continue

            records.append(
                {
                    "location_key": location_key,
                    "location": str(
                        location_config["display_name"]
                    ),
                    "month": normalized_month,
                    "collection_days": collection_days,
                    "daily_average_tonnes": (
                        str(daily_average)
                        if daily_average is not None
                        else None
                    ),
                    "total_amount_tonnes": (
                        str(total_amount)
                        if total_amount is not None
                        else None
                    ),
                    "page_number": page_number,
                    "source_file": str(path),
                }
            )

        return records

    def _resolve_location(
        self,
        *,
        document_text: str,
        requested_location_key: str | None,
    ) -> tuple[str, dict[str, Any]]:
        if requested_location_key is not None:
            location_config = (
                self.config_loader
                .get_location_config(
                    requested_location_key
                )
            )

            if not self._location_matches(
                document_text,
                location_config,
            ):
                raise PDFLocationNotFoundError(
                    f"The PDF does not appear to match "
                    f"'{location_config['display_name']}'."
                )

            return (
                requested_location_key,
                location_config,
            )

        matches: list[
            tuple[int, str, dict[str, Any]]
        ] = []

        all_locations = (
            self.config_loader
            .get_all_locations()
        )

        for location_key, location_config in (
            all_locations.items()
        ):
            match_score = (
                self._location_match_score(
                    document_text,
                    location_config,
                )
            )

            if match_score is not None:
                matches.append(
                    (
                        match_score,
                        location_key,
                        location_config,
                    )
                )

        if not matches:
            raise PDFLocationNotFoundError(
                "The PDF collection location could "
                "not be identified. Add the text "
                "found in the PDF to food_waste.yaml "
                "or pass location_key explicitly."
            )

        matches.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        highest_score = matches[0][0]

        best_matches = [
            match
            for match in matches
            if match[0] == highest_score
        ]

        if len(best_matches) > 1:
            matched_names = ", ".join(
                str(config["display_name"])
                for _, _, config in best_matches
            )

            raise PDFLocationAmbiguousError(
                f"The PDF matched multiple locations: "
                f"{matched_names}. "
                "Pass location_key explicitly."
            )

        _, location_key, location_config = (
            best_matches[0]
        )

        return location_key, location_config

    def _location_matches(
        self,
        document_text: str,
        location_config: dict[str, Any],
    ) -> bool:
        return (
            self._location_match_score(
                document_text,
                location_config,
            )
            is not None
        )

    def _location_match_score(
        self,
        document_text: str,
        location_config: dict[str, Any],
    ) -> int | None:
        normalized_document = self._normalize_text(
            document_text
        )

        identification = location_config.get(
            "identification",
            {},
        )

        excluded_terms = identification.get(
            "excluded_terms",
            [],
        )

        for excluded_term in excluded_terms:
            if (
                self._normalize_text(excluded_term)
                in normalized_document
            ):
                return None

        required_groups = identification.get(
            "required_groups",
            [],
        )

        required_score = 0

        for group in required_groups:
            normalized_candidates = [
                self._normalize_text(candidate)
                for candidate in group
                if str(candidate).strip()
            ]

            matching_candidates = [
                candidate
                for candidate in normalized_candidates
                if candidate in normalized_document
            ]

            if not matching_candidates:
                return None

            required_score += max(
                len(candidate)
                for candidate in matching_candidates
            )

        aliases = location_config.get("aliases", [])

        alias_scores = [
            len(normalized_alias)
            for alias in aliases
            if (
                normalized_alias := self._normalize_text(alias)
            )
            and normalized_alias in normalized_document
        ]

        alias_score = max(alias_scores, default=0)

        return required_score + (alias_score * 10)
    

    @classmethod
    def normalize_month(
        cls,
        value: str,
        *,
        strict: bool = True,
    ) -> str | None:
        cleaned = cls._clean_cell(value)

        match = cls.MONTH_REGEX.search(cleaned)

        if not match:
            if strict:
                raise ValueError(
                    f"Invalid month '{value}'. "
                    "Expected a value such as Apr-26."
                )

            return None

        month_name = match.group(1).title()
        year = match.group(2)

        if len(year) == 4:
            year = year[-2:]

        return f"{month_name}-{year}"

    @staticmethod
    def _extract_document_text(
        pages: Iterable[Any],
    ) -> str:
        text_parts: list[str] = []

        for page in pages:
            text = page.extract_text() or ""
            text_parts.append(text)

        document_text = "\n".join(text_parts).strip()

        if not document_text:
            raise PDFProcessingError(
                "No selectable text was extracted from the PDF. "
                "The file may be scanned and require OCR."
            )

        return document_text

    @staticmethod
    def _validate_pdf_path(
        pdf_path: str | Path,
    ) -> Path:
        path = Path(pdf_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"PDF was not found: {path}"
            )

        if not path.is_file():
            raise PDFProcessingError(
                f"The supplied path is not a file: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise PDFProcessingError(
                f"The supplied file is not a PDF: {path.name}"
            )

        return path

    @staticmethod
    def _require_column_index(
        column_map: dict[str, Any],
        column_name: str,
    ) -> int:
        value = column_map.get(column_name)

        if not isinstance(value, int) or value < 0:
            raise PDFProcessingError(
                f"Column '{column_name}' must be a "
                "non-negative integer in food_waste.yaml."
            )

        return value

    @staticmethod
    def _get_cell(
        row: list[str],
        index: int,
    ) -> str:
        if index >= len(row):
            return ""

        return row[index]

    @staticmethod
    def _clean_cell(value: Any) -> str:
        if value is None:
            return ""

        text = str(value)
        text = text.replace("\u00a0", " ")
        text = text.replace("\n", " ")

        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _normalize_text(value: Any) -> str:
        text = str(value or "").casefold()

        text = text.replace("–", "-")
        text = text.replace("—", "-")
        text = text.replace("－", "-")
        text = text.replace("\u00a0", " ")

        return re.sub(
            r"[\s\-–—－_:：,，.。/\\]+",
            "",
            text,
        )

    @staticmethod
    def _parse_integer(
        value: str,
    ) -> int | None:
        cleaned = value.replace(",", "").strip()

        if not cleaned:
            return None

        match = re.search(r"-?\d+", cleaned)

        if not match:
            return None

        return int(match.group())

    @staticmethod
    def _parse_decimal(
        value: str,
    ) -> Decimal | None:
        cleaned = value.replace(",", "").strip()

        if not cleaned:
            return None

        match = re.search(
            r"-?(?:\d+(?:\.\d+)?|\.\d+)",
            cleaned,
        )

        if not match:
            return None

        try:
            return Decimal(match.group())
        except InvalidOperation:
            return None

    @staticmethod
    def _deduplicate_records(
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        deduplicated: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}

        for record in records:
            key = (
                str(record["location_key"]),
                str(record["month"]),
            )

            existing = deduplicated.get(key)

            if existing is None:
                deduplicated[key] = record
                continue

            if (
                existing["total_amount_tonnes"] is None
                and record["total_amount_tonnes"] is not None
            ):
                deduplicated[key] = record

        return list(deduplicated.values())