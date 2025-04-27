from fastapi import HTTPException, status
from app.features.suppliers.models import Supplier
from app.features.suppliers.repositories import (
    create_supplier as repository_create_supplier,
    get_supplier as repository_get_supplier,
    get_suppliers as repository_get_suppliers,
)

from app.features.suppliers.schemas import SupplierCreate

def get_supplier_service(supplier_id: int) -> Supplier | None:
    """Get a supplier by ID."""
    supplier: Supplier | None = repository_get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    return supplier

def create_supplier_service(supplier_schema: SupplierCreate) -> Supplier:
    """Create a new supplier."""
    supplier: Supplier = Supplier(**supplier_schema.model_dump())
    repository_create_supplier(supplier)
    if not supplier.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supplier creation failed",
        )
    return supplier

def get_suppliers_service(page: int, page_size: int, name: str | None = None) -> list[Supplier]:
    """Get suppliers by page and optionally filter by name."""
    suppliers: list[Supplier] = repository_get_suppliers(page, page_size, name)
    if not suppliers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No suppliers found",
        )
    return suppliers