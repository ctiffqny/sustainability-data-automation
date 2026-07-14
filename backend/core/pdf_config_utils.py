from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


class PDFConfigError(Exception):
    """Raised when the food-waste PDF configuration is invalid."""


class PDFConfigLoader:
    def __init__(
        self,
        config_path: str | Path | None = None,
    ) -> None:
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parents[1]
                / "config"
                / "food_waste.yaml"
            )

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def reload(self) -> None:
        """Reload the YAML configuration from disk."""
        self.config = self._load_config()

    def get_defaults(self) -> dict[str, Any]:
        """Return a copy of the shared defaults."""
        return deepcopy(
            self.config.get("defaults", {})
        )

    def get_location_config(
        self,
        location_key: str,
    ) -> dict[str, Any]:
        """
        Return one location configuration merged with defaults.
        """
        locations = self.config["locations"]

        if location_key not in locations:
            available = ", ".join(
                sorted(locations)
            )

            raise PDFConfigError(
                f"Unknown location key '{location_key}'. "
                f"Available keys: {available}"
            )

        return self._merge_location_config(
            locations[location_key]
        )

    def get_all_locations(
        self,
    ) -> dict[str, dict[str, Any]]:
        """
        Return every location merged with shared defaults.
        """
        return {
            location_key: self._merge_location_config(
                location_config
            )
            for location_key, location_config
            in self.config["locations"].items()
        }

    def get_location_keys(self) -> list[str]:
        """Return all configured location keys."""
        return sorted(
            self.config["locations"].keys()
        )

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.is_file():
            raise PDFConfigError(
                "Food-waste PDF configuration was not found: "
                f"{self.config_path}"
            )

        try:
            with self.config_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                config = yaml.safe_load(file) or {}

        except yaml.YAMLError as exc:
            raise PDFConfigError(
                f"Invalid YAML in "
                f"'{self.config_path.name}': {exc}"
            ) from exc

        except OSError as exc:
            raise PDFConfigError(
                f"Could not read "
                f"'{self.config_path}': {exc}"
            ) from exc

        self._validate_config(config)

        return config

    @staticmethod
    def _validate_config(
        config: Any,
    ) -> None:
        if not isinstance(config, dict):
            raise PDFConfigError(
                "The YAML root must be a mapping."
            )

        defaults = config.get("defaults")

        if not isinstance(defaults, dict):
            raise PDFConfigError(
                "The YAML must contain a "
                "'defaults' mapping."
            )

        locations = config.get("locations")

        if not isinstance(locations, dict):
            raise PDFConfigError(
                "The YAML must contain a "
                "'locations' mapping."
            )

        if not locations:
            raise PDFConfigError(
                "The YAML contains no locations."
            )

        default_columns = defaults.get(
            "columns",
            {},
        )

        required_columns = {
            "month",
            "collection_days",
            "daily_average",
            "total_amount",
        }

        missing_columns = (
            required_columns
            - set(default_columns)
        )

        if missing_columns:
            raise PDFConfigError(
                "The default column mapping is missing: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        for location_key, location in (
            locations.items()
        ):
            if not isinstance(location, dict):
                raise PDFConfigError(
                    f"Location '{location_key}' "
                    "must be a mapping."
                )

            display_name = location.get(
                "display_name"
            )

            if not display_name:
                raise PDFConfigError(
                    f"Location '{location_key}' "
                    "needs a display_name."
                )

            identification = location.get(
                "identification",
                {},
            )

            required_groups = (
                identification.get(
                    "required_groups",
                    [],
                )
            )

            if not required_groups:
                raise PDFConfigError(
                    f"Location '{location_key}' "
                    "needs identification."
                    "required_groups."
                )

    def _merge_location_config(
        self,
        location_config: dict[str, Any],
    ) -> dict[str, Any]:
        defaults = deepcopy(
            self.config.get("defaults", {})
        )

        location = deepcopy(
            location_config
        )

        return self._deep_merge(
            defaults,
            location,
        )

    @classmethod
    def _deep_merge(
        cls,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        result = deepcopy(base)

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = cls._deep_merge(
                    result[key],
                    value,
                )
            else:
                result[key] = deepcopy(value)

        return result