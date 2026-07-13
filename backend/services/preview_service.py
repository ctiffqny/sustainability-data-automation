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


def build_preview_response(category, source_file, target_file):
    category = category.lower().strip()
    run_id = str(uuid.uuid4())

    config, config_path = load_category_config(category)

    source_path = save_upload(source_file)
    target_path = save_upload(target_file)

    config["source_file"] = str(source_path)
    config["target_file"] = str(target_path)

    config["source_output_file"] = str(
        OUTPUT_DIR / f"{run_id}_{category}_source_highlighted.xlsx"
    )
    config["target_output_file"] = str(
        OUTPUT_DIR / f"{run_id}_{category}_preview_output.xlsx"
    )

    if category == "electricity":
        result = preview_electricity_transfer(config)

    elif category == "recyclable_wastes":
        result = preview_recyclable_wastes_transfer(config)

    else:
        return {
            "status": "error",
            "message": f"Unsupported category: {category}",
        }

    result["status"] = "success"
    result["category"] = category
    result["source_path"] = str(source_path)
    result["target_path"] = str(target_path)
    result["config_used"] = config_path.name
    result["run_id"] = run_id

    return result

def build_apply_response(
    category,
    source_path,
    target_path,
):
    category = category.lower().strip()

    run_id = str(uuid.uuid4())

    config, config_path = load_category_config(category)

    config["source_file"] = source_path

    # Duplicate starts from the uploaded target copy.
    config["target_file"] = target_path

    config["target_output_file"] = str(
        OUTPUT_DIR
        / f"{run_id}_{category}_applied_output.xlsx"
    )

    config["source_output_file"] = str(
        OUTPUT_DIR
        / f"{run_id}_{category}_source_highlighted.xlsx"
    )

    if category == "electricity":
        result = apply_electricity_transfer(
            config,
        )

    elif category == "recyclable_wastes":
        result = apply_recyclable_wastes_transfer(
            config,
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
    result["source_path"] = source_path
    result["target_path"] = config["target_file"]
    result["output_file"] = config["target_output_file"]
    result["highlighted_source_file"] = (
        config["source_output_file"]
    )

    result["message"] = (
        "A duplicate workbook was created successfully."
    )

    return result