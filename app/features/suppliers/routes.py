from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_session
from app.features.suppliers.models import *
from app.features.suppliers.schemas import *
from app.features.suppliers.services import *

router = APIRouter(prefix="/suppliers", tags=["suppliers"], dependencies=[Depends(get_session)])

@router.get("/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: int) -> Supplier | None:
    """Get a supplier by ID."""
    try:
        supplier: Supplier | None = get_supplier_service(supplier_id)
        return supplier
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error
    
@router.post("/", response_model=Supplier)
async def create_supplier(supplier: SupplierCreate) -> Supplier:
    """Create a new supplier."""
    try:
        new_supplier: Supplier = create_supplier_service(supplier)
        return new_supplier
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supplier creation failed",
        ) from error
    
@router.get("/", response_model=list[Supplier])
async def get_suppliers(page: int = 1, name: str | None = None) -> list[Supplier]:
    """Get suppliers by page and optionally filter by name."""
    try:
        suppliers: list[Supplier] = get_suppliers_service(page, 10, name)
        return suppliers
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error