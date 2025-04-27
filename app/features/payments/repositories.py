from sqlmodel import select
from app.core.database import SessionDep, db_session
from app.features.suppliers.models import Supplier

def create_supplier(supplier: Supplier) -> None:
    """Create a supplier."""
    session: SessionDep = db_session.get()
    session.add(supplier)
    session.commit()

def get_supplier(supplier_id: int) -> Supplier | None:
    """Get a supplier by ID."""
    session: SessionDep = db_session.get()
    statement = select(Supplier).where(Supplier.id == supplier_id)
    result = session.exec(statement).first()
    return result

def get_suppliers(page: int, page_size: int, name: str | None = None) -> list[Supplier]:
    """Get suppliers by page and optionally filter by name."""
    session: SessionDep = db_session.get()
    statement = select(Supplier).offset((page - 1) * page_size).limit(page_size)
    if name:
        statement = statement.where(Supplier.name.contains(name)) # type: ignore
    result = session.exec(statement).all()
    return list(result)