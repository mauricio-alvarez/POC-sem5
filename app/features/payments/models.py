from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from app.features.products.models import Product

if TYPE_CHECKING:
    from app.features.products.models import Product

class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers" #type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    phone: str = Field(unique=True, index=True, nullable=False)
    address: str = Field(nullable=False)
    city: str = Field(nullable=False)
    state: str = Field(nullable=False)
    country: str = Field(nullable=False)
    postal_code: str = Field(nullable=False)
    is_active: bool = Field(default=True)

    products: List["Product"] = Relationship(back_populates="supplier")
