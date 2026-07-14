from pathlib import Path

from backend.processors.pdf_processor import PDFProcessor


def main() -> None:
    project_root = Path(__file__).resolve().parent

    pdf_path = (
        project_root
        / "ref"
        / "test_food_waste_pdf"
        / "2026年4月（香港科技大學 - LG 7 百佳）厨餘收集數據.pdf"
    )

    processor = PDFProcessor()

    print("Testing file:")
    print(pdf_path)
    print()

    location = processor.identify_location(pdf_path)

    print("Detected location:")
    print(location)
    print()

    record = processor.extract_record(
        pdf_path,
        month="Apr-26",
    )

    print("Extracted record:")
    print(record)
    print()

    total = processor.extract_total_amount(
        pdf_path,
        month="Apr-26",
    )

    print("Total amount:")
    print(total)


if __name__ == "__main__":
    main()