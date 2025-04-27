from typing import Optional, List, TYPE_CHECKING 
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.features.suppliers.models import Supplier

class Product(SQLModel, table=True):
    __tablename__ = "products" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    description: str = Field(nullable=False)
    price: float = Field(nullable=False)
    stock: int = Field(nullable=False)

    supplier_id: Optional[int] = Field(default=None, foreign_key="suppliers.id", index=True) 
    supplier: Optional["Supplier"] = Relationship(back_populates="products")



