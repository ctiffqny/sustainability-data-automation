from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.services.preview_service import build_preview_response, build_apply_response
from backend.services.preview_service import build_preview_response
from fastapi.responses import FileResponse
from pathlib import Path

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


@app.get("/")
def root():
    return {"status": "Backend is connected"}


@app.post("/preview")
async def preview(
    category: str = Form(...),
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...),
):
    try:
        return build_preview_response(
            category,
            source_file,
            target_file,
        )
    except (FileNotFoundError, ValueError) as error:
        return {
            "status": "error",
            "message": str(error),
        }
    

@app.post("/apply")
async def apply(
    category: str = Form(...),
    source_path: str = Form(...),
    target_path: str = Form(...),
    output_mode: str = Form("duplicate"),
):
    try:
        return build_apply_response(
            category=category,
            source_path=source_path,
            target_path=target_path,
            output_mode=output_mode,
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