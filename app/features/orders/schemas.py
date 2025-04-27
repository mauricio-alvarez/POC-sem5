from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from .models import OrderStatus # Import the enum

class ProductPurchaseItem(BaseModel):
    product_id: int = Field(..., ge=1, description="ID of the product to purchase")
    amount: int = Field(..., gt=0, description="Quantity of the product")

class ClientOrderPurchaseRequest(BaseModel):
    products: List[ProductPurchaseItem] = Field(..., min_items=1, description="List of products and their amounts")

class CustomProductCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Name of the custom product")
    description: str = Field(..., min_length=5, description="Description of the custom product request")

class ClientOrderCustomRequest(BaseModel):
    product: CustomProductCreate = Field(..., description="Details of the custom product to order")

class ProductInOrder(BaseModel):
    product_id: int
    name: str
    amount: int
    unit_price: float

class ClientOrderReadBase(BaseModel):
    id: int
    client_id: int
    total_price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClientOrderReadDetails(ClientOrderReadBase):
    products: List[ProductInOrder] = []

class SupplierOrderReadBase(BaseModel):
    id: int
    supplier_id: int
    product_id: int
    amount: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SupplierOrderReadDetails(SupplierOrderReadBase):
    supplier_name: Optional[str] = None
    product_name: Optional[str] = None

class OrderCreateResponse(BaseModel):
    message: str = "Order created successfully"
    order_id: int

class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List