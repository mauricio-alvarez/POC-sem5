from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String
from datetime import datetime
import enum

from app.features.auth.models import User
from app.features.products.models import Product
from app.features.suppliers.models import Supplier 


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CUSTOM_PENDING = "custom_pending"

class ClientOrder(SQLModel, table=True):
    __tablename__ = "client_orders" 

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    total_price: float = Field(default=0.0, nullable=False)

    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
        sa_column=Column(String(50), nullable=False) 
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    client: User = Relationship()
    product_links: List["ClientOrderProduct"] = Relationship(back_populates="order")

# Link Table: M2M between ClientOrder and Product
class ClientOrderProduct(SQLModel, table=True):
    __tablename__ = "client_order_products" 

    order_id: Optional[int] = Field(default=None, foreign_key="client_orders.id", primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="products.id", primary_key=True)
    amount: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)

    order: ClientOrder = Relationship(back_populates="product_links")
    product: Product = Relationship()


# --- Supplier Order Models ---
class SupplierOrder(SQLModel, table=True):
    __tablename__ = "supplier_orders" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="suppliers.id", index=True, nullable=False)
    product_id: int = Field(foreign_key="products.id", index=True, nullable=False)
    amount: int = Field(default=1, nullable=False)
    total_price: float = Field(nullable=False) # Price paid TO supplier
    status: str = Field(default="placed", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    supplier: Supplier = Relationship()
    product: Product = Relationship()