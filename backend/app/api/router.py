from fastapi import APIRouter
from app.api import auth, brands, models, colors, formulas, components, imports, audit, stats

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(models.router, prefix="/models", tags=["Vehicle Models"])
api_router.include_router(colors.router, prefix="/colors", tags=["Colors"])
api_router.include_router(components.router, prefix="/components", tags=["Components"])
api_router.include_router(formulas.router, prefix="/formulas", tags=["Formulas"])
api_router.include_router(imports.router, prefix="/admin/import", tags=["Data Import"])
api_router.include_router(audit.router, prefix="/admin/audit", tags=["Audit Log"])
api_router.include_router(stats.router, prefix="/admin/stats", tags=["Admin Dashboard"])
