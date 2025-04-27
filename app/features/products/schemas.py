from pydantic import BaseModel, EmailStr, Field

class ProductCreate(BaseModel):
    name: str = Field(..., description="Name of the product")
    description: str = Field(..., description="Description of the product")
    price: float = Field(..., description="Price of the product")
    stock: int = Field(..., description="Stock available")
    supplier_id: int = Field(..., description="ID of the supplier that owns the product")
