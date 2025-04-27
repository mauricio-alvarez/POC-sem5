from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_session
from app.features.products.models import *
from app.features.products.schemas import *
from app.features.products.services import *

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_session)])

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int) -> Product | None:
    """Get a product by ID."""
    try:
        product: Product | None = get_product_service(product_id)
        return product
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

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate) -> Product:
    """Create a new product."""
    try:
        new_product: Product = create_product_service(product)
        return new_product
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product creation failed",
        ) from error
    
@router.get("/", response_model=list[Product])
async def get_products(page: int = 1, name: str | None = None) -> list[Product]:
    """Get products by page and optionally filter by name."""
    try:
        products: list[Product] = get_products_service(page, 10, name)
        return products
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