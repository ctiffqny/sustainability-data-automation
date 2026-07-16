from pathlib import Path
import shutil
import uuid
import yaml

from backend.processors.electricity_processor import (
    preview_electricity_transfer,
    apply_electricity_transfer,
)

from backend.processors.recyclable_wastes_processor import (
    preview_recyclable_wastes_transfer,
    apply_recyclable_wastes_transfer,
)

from backend.processors.food_waste_processor import (
    preview_food_waste_transfer,
    apply_food_waste_transfer,
)

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "outputs"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_category_config(category: str):
    category = category.lower().strip()
    config_path = CONFIG_DIR / f"{category}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"No config found for category: {category}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config, config_path


def save_upload(upload_file):
    run_file_id = str(uuid.uuid4())
    safe_filename = upload_file.filename.replace(" ", "_")
    file_path = TEMP_DIR / f"{run_file_id}_{safe_filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path


def build_preview_response(
    category,
    source_file=None,
    target_file=None,
    source_files=None,
    smart_bin_file=None,
    smart_bin_collection_point=None,
    month=None,
):
    category = category.lower().strip()
    run_id = str(uuid.uuid4())

    config, config_path = load_category_config(
        category
    )

    target_path = save_upload(target_file)

    config["target_file"] = str(target_path)
    config["config_path"] = str(config_path)

    config["target_output_file"] = str(
        OUTPUT_DIR
        / f"{run_id}_{category}_preview_output.xlsx"
    )

    if category == "food_waste":
        if not source_files:
            return {
                "status": "error",
                "message": (
                    "At least one food-waste PDF "
                    "must be uploaded."
                ),
            }
        
        print(f"Received {len(source_files)} food-waste PDFs")

        source_paths = save_uploads(source_files)

        print("Saved uploaded PDFs:")
        for path in source_paths:
            print(path)

        config["source_files"] = [
            str(path)
            for path in source_paths
        ]
        config["month"] = month

        if smart_bin_file is not None:
            smart_bin_path = save_upload(smart_bin_file)
            config["smart_bin_source_file"] = str(smart_bin_path)
            config["smart_bin_collection_point"] = smart_bin_collection_point
        else:
            smart_bin_path = None

        print("Starting food-waste preview")

        result = preview_food_waste_transfer(config)
        print("Food-waste preview completed")

        result["source_paths"] = [
            str(path)
            for path in source_paths
        ]
        result["smart_bin_path"] = str(smart_bin_path) if smart_bin_path else None
        result["smart_bin_collection_point"] = smart_bin_collection_point

    else:
        source_path = save_upload(source_file)

        config["source_file"] = str(source_path)

        config["source_output_file"] = str(
            OUTPUT_DIR
            / (
                f"{run_id}_{category}"
                "_source_highlighted.xlsx"
            )
        )

        if category == "electricity":
            result = preview_electricity_transfer(
                config
            )

        elif category == "recyclable_wastes":
            result = (
                preview_recyclable_wastes_transfer(
                    config
                )
            )

        else:
            return {
                "status": "error",
                "message": (
                    f"Unsupported category: {category}"
                ),
            }

        result["source_path"] = str(
            source_path
        )

    result["status"] = "success"
    result["category"] = category
    result["target_path"] = str(target_path)
    result["config_used"] = config_path.name
    result["run_id"] = run_id

    return result


def build_apply_response(
    category,
    target_path,
    source_path=None,
    source_paths=None,
    smart_bin_path=None,
    smart_bin_collection_point=None,
    month=None,
):
    category = category.lower().strip()
    run_id = str(uuid.uuid4())

    config, config_path = load_category_config(
        category
    )

    config["target_file"] = target_path
    config["config_path"] = str(config_path)

    config["target_output_file"] = str(
        OUTPUT_DIR
        / f"{run_id}_{category}_applied_output.xlsx"
    )

    if category == "food_waste":
        config["source_files"] = source_paths or []
        config["month"] = month
        if smart_bin_path:
            config["smart_bin_source_file"] = smart_bin_path
            config["smart_bin_collection_point"] = smart_bin_collection_point

        result = apply_food_waste_transfer(
            config
        )

    else:
        config["source_file"] = source_path

        config["source_output_file"] = str(
            OUTPUT_DIR
            / (
                f"{run_id}_{category}"
                "_source_highlighted.xlsx"
            )
        )

        if category == "electricity":
            result = apply_electricity_transfer(
                config
            )

        elif category == "recyclable_wastes":
            result = (
                apply_recyclable_wastes_transfer(
                    config
                )
            )

        else:
            return {
                "status": "error",
                "message": (
                    f"Unsupported category: {category}"
                ),
            }

    result["status"] = "success"
    result["category"] = category
    result["config_used"] = config_path.name
    result["run_id"] = run_id
    result["target_path"] = target_path
    result["output_file"] = (
        config["target_output_file"]
    )
    result["message"] = (
        "A duplicate workbook was created successfully."
    )

    return result

def save_uploads(upload_files):
    return [
        save_upload(upload_file)
        for upload_file in upload_files
    ]