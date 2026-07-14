from __future__ import annotations

from pathlib import Path
import shutil
import uuid

from backend.processors.pdf_processor import PDFProcessor


BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_DIR = BASE_DIR / "temp"

TEMP_DIR.mkdir(parents=True, exist_ok=True)

pdf_processor = PDFProcessor()


def save_pdf_upload(upload_file) -> Path:
    filename = Path(upload_file.filename or "upload.pdf").name

    if Path(filename).suffix.lower() != ".pdf":
        raise ValueError(
            f"'{filename}' is not a PDF file."
        )

    file_id = str(uuid.uuid4())
    safe_filename = filename.replace(" ", "_")
    file_path = TEMP_DIR / f"{file_id}_{safe_filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            upload_file.file,
            buffer,
        )

    return file_path



def build_food_waste_record_response(
    pdf_file,
    month: str,
    location_key: str | None = None,
) -> dict:
    """
    Save an uploaded PDF and extract one monthly record.
    """
    pdf_path = save_pdf_upload(pdf_file)

    try:
        record = pdf_processor.extract_record(
            pdf_path=pdf_path,
            month=month,
            location_key=location_key,
        )

        return {
            "status": "success",
            **record,
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "source_path": str(pdf_path),
        }


def build_food_waste_total_response(
    pdf_file,
    month: str,
    location_key: str | None = None,
) -> dict:
    """
    Save an uploaded PDF and return only the monthly total.
    """
    pdf_path = save_pdf_upload(pdf_file)

    try:
        total = pdf_processor.extract_total_amount(
            pdf_path=pdf_path,
            month=month,
            location_key=location_key,
        )

        location = pdf_processor.identify_location(pdf_path)

        return {
            "status": "success",
            "location_key": location["location_key"],
            "location": location["location"],
            "month": PDFProcessor.normalize_month(month),
            "total_amount_tonnes": str(total),
            "source_path": str(pdf_path),
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "source_path": str(pdf_path),
        }


def build_all_food_waste_months_response(
    pdf_file,
    location_key: str | None = None,
) -> dict:
    """
    Save an uploaded PDF and extract every populated month.
    """
    pdf_path = save_pdf_upload(pdf_file)

    try:
        records = pdf_processor.extract_all_months(
            pdf_path=pdf_path,
            location_key=location_key,
        )

        return {
            "status": "success",
            "record_count": len(records),
            "records": records,
            "source_path": str(pdf_path),
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "source_path": str(pdf_path),
        }


def build_food_waste_location_response(
    pdf_file,
) -> dict:
    """
    Save an uploaded PDF and identify its configured location.
    """
    pdf_path = save_pdf_upload(pdf_file)

    try:
        location = pdf_processor.identify_location(pdf_path)

        return {
            "status": "success",
            **location,
            "source_path": str(pdf_path),
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "source_path": str(pdf_path),
        }
    
