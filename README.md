# Sustainability Data Automation

Built for the **HKUST Sustainability and Net-Zero Office**.

The Sustainability Data Automation System automates the extraction and transfer of sustainability data from supplier reports into the HKUST Sustainability Master Workbook.

Previously, sustainability data was manually extracted from monthly supplier reports and entered into the master workbook. This application automates the extraction, validation, preview, and transfer process while preserving workbook formatting, formulas, and calculations.

## Supported Categories

- Electricity
- Recyclable Waste
- Food Waste

## Features

- Upload supplier PDF and Excel reports
- Automatic data extraction
- Preview extracted values before applying changes
- Generate an updated copy of the Sustainability Master Workbook
- Preserve workbook formatting and formulas
- Automatic recalculation after data transfer
- Smart Waste-bin integration for Food Waste
- Configuration-driven mappings using YAML files
- Modular architecture for future sustainability categories

## Project Structure

```text
backend/
├── api/
├── config/
├── core/
├── models/
├── processors/
├── services/
├── uploads/
├── outputs/
└── main.py

frontend/
├── public/
└── src/
    ├── components/
    └── App.jsx

ref/
├── Sample Reports
├── Master Workbook
└── Testing Files
```

## Technology Stack

### Backend

- Python
- FastAPI
- OpenPyXL
- pandas
- pdfplumber
- PyYAML

### Frontend

- React
- Vite
- Axios

# Getting Started

## 1. Fork the Repository

Future staff members and interns should **fork** this repository before making any changes.

Forking preserves the original project while allowing independent development.

## 2. Clone Your Fork

```bash
git clone https://github.com/<your-github-username>/sustainability-data-automation.git

cd sustainability-data-automation
```

## 3. Backend Setup

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run FastAPI

```bash
uvicorn backend.main:app --reload
```

## 4. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

The application is available at

```
http://localhost:5173
```

# Supported Workflows

## Electricity

- Upload electricity Excel reports
- Review extracted values
- Preview workbook changes
- Generate an updated workbook

## Recyclable Waste

- Upload recyclable waste reports
- Review extracted values
- Preview workbook changes
- Generate an updated workbook

## Food Waste

Food Waste combines two data sources:

1. Supplier Food Waste reports
2. Smart Waste-bin transaction workbook

Business rules:

- Student Hall and Jockey Club Global Graduate Tower are aggregated into **UG Halls + Seafront Cafeteria**.
- Staff Quarter(s) and PRQS are aggregated into **Staff Quarters (All)**.
- All Smart Waste-bin food waste is deducted from the selected collection point.
- Staff Quarter supplier reports are intentionally ignored to prevent double counting.

# Known Business Rules

These rules reflect the Sustainability Office's reporting workflow and should not be modified without confirmation from the data owners.

## General

- Always duplicate the master workbook before editing.
- Preserve workbook formatting and formulas.
- Store all transferred values in kilograms (kg).
- Match reporting periods by month.
- Create a new row if the reporting month does not exist.
- Update only mapped cells.

## Food Waste

- Supplier reports provide the collection point totals.
- Smart Waste-bin data supplements supplier reports.
- Student Hall and JCGGT values are added to **UG Halls + Seafront Cafeteria**.
- Staff Quarter(s) and PRQS values are added to **Staff Quarters (All)**.
- All Smart Waste-bin food waste is deducted from one user-selected collection point.
- Staff Quarter supplier reports are ignored to prevent double counting.

# Where to Make Changes

| Task | File(s) |
|------|----------|
| Supplier report mappings | `backend/config/*.yaml` |
| Food Waste business logic | `backend/processors/food_waste_processor.py` |
| Electricity processing | `backend/processors/electricity_processor.py` |
| Recyclable Waste processing | `backend/processors/recyclable_wastes_processor.py` |
| Workbook calculations | `backend/processors/calculation_processor.py` |
| PDF extraction | `backend/processors/pdf_processor.py` |
| Preview & Apply workflow | `backend/services/preview_service.py` |
| API endpoints | `backend/main.py` |
| Frontend upload workflow | `frontend/src/components/` |

# Reference Files

Sample reports and testing workbooks are located in

```
ref/
```

Use these files whenever testing new functionality.

# Adding a New Sustainability Category

1. Create a new YAML configuration in `backend/config/`.
2. Create a processor in `backend/processors/`.
3. Register the processor in the Preview/Apply service.
4. Add the upload interface to the frontend.
5. Test using representative reports.

# Troubleshooting

### Backend shows "Network Error"

- Ensure FastAPI is running.
- Verify the frontend backend URL.
- Check browser Developer Tools.
- Check the backend terminal for exceptions.

### Workbook output is incorrect

- Verify the reporting month.
- Confirm the supplier report layout has not changed.
- Check the corresponding YAML configuration.
- Verify the selected Food Waste collection point.

# Future Improvements

- Additional sustainability categories
- Batch processing
- Automated regression tests
- Improved validation and error reporting
- Dashboard and analytics
- User authentication

# Acknowledgements

Developed for the **HKUST Sustainability and Net-Zero Office** to streamline sustainability reporting, reduce manual processing, improve data consistency, and support the University's sustainability reporting workflow.

Special thanks to Marcus, Lily, Teri, Michael, Cyrus, and the rest of the Sustainability and Net-Zero Office for their guidance, feedback, and support throughout the development of this project.

# Maintainer Notes

If you are a future staff member or intern:

- Read this README before making changes.
- Test every modification using the sample files in `ref/`.
- Keep business rules separate from implementation logic.
- Confirm reporting requirement changes with the Sustainability and Net-Zero Office before modifying the code.
- Commit changes frequently and document significant updates.