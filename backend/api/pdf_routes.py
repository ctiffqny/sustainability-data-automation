from fastapi import (
    APIRouter,
    File,
    Form,
    UploadFile,
)

from backend.services.pdf_service import (
    process_uploaded_pdfs,
)


router = APIRouter(
    prefix="/food-waste",
    tags=["Food Waste"],
)


@router.post("/multiple")
def extract_multiple_food_waste_pdfs(
    month: str = Form(...),
    pdf_files: list[UploadFile] = File(...),
):
    return process_uploaded_pdfs(
        pdf_files=pdf_files,
        month=month,
    )