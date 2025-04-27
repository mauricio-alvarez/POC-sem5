from sqlmodel import select
from app.core.database import SessionDep, db_session
from app.features.products.models import Product


def create_product(product: Product) -> None:
    """Create a product."""
    session: SessionDep = db_session.get()
    session.add(product)
    session.commit()

def get_product(product_id: int) -> Product | None:
    """Get a product by ID."""
    session: SessionDep = db_session.get()
    statement = select(Product).where(Product.id == product_id)
    result = session.exec(statement).first()
    return result

def get_products(page: int, page_size: int, name: str | None = None) -> list[Product]:
    """Get products by page and optionally filter by name."""
    session: SessionDep = db_session.get()
    statement = select(Product).offset((page - 1) * page_size).limit(page_size)
    if name:
        statement = statement.where(Product.name.contains(name)) # type: ignore
    result = session.exec(statement).all()
    return list(result)