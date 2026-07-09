from backend.processors.electricity_processor import process_electricity
from backend.processors.recyclable_wastes_processor import process_recyclable_wastes


def run_excel_transfer(config):
    category = config["category"].lower()
    print(f">>> category is: {repr(category)}")

    processors = {
        "electricity": process_electricity,
        "recyclable_wastes": process_recyclable_wastes,
    }

    if category not in processors:
        raise ValueError(f"Unknown category: {category}")

    processors[category](config)