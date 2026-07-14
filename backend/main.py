from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.services.preview_service import build_preview_response, build_apply_response
from backend.services.preview_service import build_preview_response
from fastapi.responses import FileResponse
from pathlib import Path
from backend.api.pdf_routes import router as pdf_router

app = FastAPI(title="Sustainability Data Automation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)

@app.get("/")
def root():
    return {"status": "Backend is connected"}


@app.post("/preview")
def preview(
    category: str = Form(...),
    target_file: UploadFile = File(...),
    source_file: UploadFile | None = File(None),
    source_files: list[UploadFile] | None = File(None),
    month: str | None = Form(None),
):
    return build_preview_response(
        category=category,
        source_file=source_file,
        source_files=source_files,
        target_file=target_file,
        month=month,
    )
    

@app.post("/apply")
async def apply(
    category: str = Form(...),
    source_path: str = Form(...),
    target_path: str = Form(...),
):
    try:
        return build_apply_response(
            category=category,
            source_path=source_path,
            target_path=target_path,
        )
    except FileNotFoundError as error:
        return {
            "status": "error",
            "message": str(error),
        }
    

@app.get("/download")
def download(file_path: str):
    path = Path(file_path)

    if not path.exists():
        return {
            "status": "error",
            "message": "File not found",
        }

    return FileResponse(
        path=path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )