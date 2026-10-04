from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.import_schema import ImportPreviewResponse, ImportConfirmRequest, ImportResultResponse
from app.services.import_service import ImportService
from app.auth.deps import get_current_active_admin

router = APIRouter()


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_data_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """
    Step 1 of Import: Upload CSV or XLSX, validate all rows,
    check required columns, calculate formulas, and return preview.
    Does NOT modify the database yet.
    """
    contents = await file.read()
    return ImportService.parse_and_validate_file(
        file_contents=contents,
        filename=file.filename or "import.csv",
        db=db,
    )


@router.post("/confirm", response_model=ImportResultResponse)
def confirm_data_import(
    req: ImportConfirmRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """
    Step 2 of Import: Commit verified batch into the database.
    Creates Brands, Models, Colors, Formulas, and FormulaComponents transactionally.
    """
    try:
        return ImportService.commit_import(
            batch_id=req.batch_id,
            db=db,
            user_email=admin.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/template")
def download_import_template():
    """Download standard sample CSV template for automotive paint formula data entry"""
    sample_csv = (
        "brand,model,year,color_code,color_name,color_type,paint_system,variant,component_code,component_name,amount,unit\n"
        "Toyota,Camry,2021,1G3,Magnetic Gray,Metallic,Basecoat,Standard,B001,White Base,350.00,g\n"
        "Toyota,Camry,2021,1G3,Magnetic Gray,Metallic,Basecoat,Standard,B014,Black,220.00,g\n"
        "Toyota,Camry,2021,1G3,Magnetic Gray,Metallic,Basecoat,Standard,M003,Metallic,180.00,g\n"
        "Toyota,Camry,2021,1G3,Magnetic Gray,Metallic,Basecoat,Standard,K002,Deep Blue Toner,100.00,g\n"
        "Toyota,Camry,2021,1G3,Magnetic Gray,Metallic,Basecoat,Standard,X001,Transparent Binder,150.00,g\n"
        "Mercedes-Benz,E-Class,2022,197,Obsidian Black,Metallic,Basecoat,Standard,B014,Black,750.00,g\n"
        "Mercedes-Benz,E-Class,2022,197,Obsidian Black,Metallic,Basecoat,Standard,M003,Metallic,150.00,g\n"
        "Mercedes-Benz,E-Class,2022,197,Obsidian Black,Metallic,Basecoat,Standard,X001,Transparent Binder,100.00,g\n"
    )
    return Response(
        content=sample_csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=paint_formula_import_template.csv"},
    )
