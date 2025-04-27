from fastapi import HTTPException, status
from app.features.products.models import Product
from app.features.products.repositories import (
    create_product as repository_create_product,
    get_product as repository_get_product,
    get_products as repository_get_products,
)
from app.features.products.schemas import ProductCreate

def get_product_service(product_id: int) -> Product | None:
    """Get a product by ID."""
    product: Product | None = repository_get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product

def create_product_service(product_schema: ProductCreate) -> Product:
    """Create a new product."""
    product: Product = Product(**product_schema.model_dump())
    repository_create_product(product)
    if not product.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product creation failed",
        )
    return product

def get_products_service(page: int, page_size: int, name: str | None = None) -> list[Product]:
    """Get products by page and optionally filter by name."""
    products: list[Product] = repository_get_products(page, page_size, name)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found",
        )
    return products

