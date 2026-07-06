import yaml
from processors.excel_processor import run_excel_transfer


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config = load_config("config/recyclable_wastes.yaml")
    run_excel_transfer(config)