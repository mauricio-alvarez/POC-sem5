from fastapi import HTTPException, status
from typing import List, Optional
import math

from . import repositories as repo
from .models import ClientOrder, Product, OrderStatus, SupplierOrder, ClientOrderProduct
from .schemas import (
    ClientOrderPurchaseRequest, ClientOrderCustomRequest, OrderCreateResponse,
    ClientOrderReadBase, ClientOrderReadDetails, ProductInOrder, PaginatedResponse,
    SupplierOrderReadBase, SupplierOrderReadDetails, CustomProductCreate
)
from app.features.auth.models import User
from app.features.products.models import Product as ProductModel # Alias if needed
from app.features.products.schemas import ProductCreate # For custom product

def _check_is_admin(user_id: int) -> User:
    """Fetches user and checks if they have the 'admin' role"""
    user = repo.get_user_with_roles(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if "admin" not in [role.title for role in user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user

# Client Order logic
def create_purchase_order_service(
    user_id: int, order_data: ClientOrderPurchaseRequest
    ) -> OrderCreateResponse:
    """Creates a standard client order."""
    total_price = 0.0
    product_ids = [item.product_id for item in order_data.products]
    products_to_update_stock = {}

    # 1. Fetch and Validate Products (Repo gets session)
    products_in_db = repo.get_products_by_ids(product_ids)
    if len(products_in_db) != len(set(product_ids)):
        found_ids = {p.id for p in products_in_db}
        missing_ids = [pid for pid in product_ids if pid not in found_ids]
        raise HTTPException(status_code=404, detail=f"Products not found: {missing_ids}")

    product_map = {p.id: p for p in products_in_db}

    # 2. Check Stock and Calculate Total Price
    for item in order_data.products:
        product = product_map.get(item.product_id)
        if not product: raise HTTPException(status_code=500, detail="Internal error")
        if product.stock < item.amount:
            raise HTTPException(400, f"Insufficient stock for {product.name}")
        total_price += product.price * item.amount
        products_to_update_stock[product.id] = item.amount

    # 3. Create Order Record
    new_order_model = ClientOrder(
        client_id=user_id, total_price=round(total_price, 2), status=OrderStatus.CONFIRMED
    )
    created_order = repo.create_client_order(new_order_model) # Repo commits
    if not created_order or not created_order.id:
        raise HTTPException(status_code=500, detail="Failed to create order record")

    order_id = created_order.id

    # 4. Create Links and Update Stock
    try:
        for item in order_data.products:
            product = product_map[item.product_id]
            repo.add_product_to_client_order( 
                order_id=order_id,
                product_id=item.product_id,
                amount=item.amount,
                unit_price=product.price
            )
            stock_updated = repo.update_product_stock(item.product_id, item.amount)
            if not stock_updated:
                 print(f"Failed to update stock for product {item.product_id} in order {order_id}")
                 raise HTTPException(status_code=500, detail=f"Stock update failed for product {item.product_id}, order partially processed.")

    except Exception as e:
         print(f"Error in order: {order_id}: {e}")
         if isinstance(e, HTTPException): raise e
         raise HTTPException(status_code=500, detail="Error processing order items/stock.")


    return OrderCreateResponse(order_id=order_id)

# Custom Clien Order logic
def create_custom_order_service(
    user_id: int, custom_data: ClientOrderCustomRequest
) -> OrderCreateResponse:
    """Creates custom product and order. Repos handle commits."""
    # 1. Create custom product 
    product_schema = ProductCreate(
        name=custom_data.product.name,
        description=custom_data.product.description,
        price=0.0, stock=1, supplier_id=None
    )
    repo.create_product(ProductModel(**product_schema.model_dump()))
    session = db_session.get() 
    created_product = session.exec(
        select(ProductModel).where(ProductModel.name == custom_data.product.name).order_by(ProductModel.id.desc())
    ).first()
    if not created_product or not created_product.id:
         raise HTTPException(status_code=500, detail="Failed to create/retrieve custom product record")
    product_id = created_product.id


    # 2. Create client order
    new_order_model = ClientOrder(
        client_id=user_id, total_price=0.0, status=OrderStatus.CUSTOM_PENDING
    )
    created_order = repo.create_client_order(new_order_model)
    if not created_order or not created_order.id:
        raise HTTPException(status_code=500, detail="Failed to create order record for custom product")
    order_id = created_order.id

    # 3. Link product to order
    try:
        repo.add_product_to_client_order(
            order_id=order_id, product_id=product_id, amount=1, unit_price=0.0
        )
    except Exception as e:
        print(f"CRITICAL WARNING: Failed to link product {product_id} to order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to link custom product to order.")

    return OrderCreateResponse(order_id=order_id)


def get_client_order_details_service(
    user_id: int, order_id: int, is_admin: bool = False
) -> ClientOrderReadDetails:
    """Gets detailed order info. Repo gets session."""
    order = repo.get_client_order_by_id(order_id=order_id, client_id=user_id, is_admin=is_admin)
    if not order:
        detail = "Order not found" if is_admin else "Order not found or access denied"
        raise HTTPException(status_code=404, detail=detail)

    products_in_order = [
        ProductInOrder(
            product_id=link.product.id, name=link.product.name,
            amount=link.amount, unit_price=link.unit_price
        ) for link in order.product_links if link.product
    ]

    return ClientOrderReadDetails(
        id=order.id, client_id=order.client_id, total_price=order.total_price,
        status=order.status, created_at=order.created_at, updated_at=order.updated_at,
        products=products_in_order
    )

def list_client_orders_service(
    user_id: int, page: int = 1, page_size: int = 10, state: Optional[OrderStatus] = None
) -> PaginatedResponse:
    """Lists client's orders"""
    orders, total_items = repo.get_client_orders_paginated(
        client_id=user_id, status=state, page=page, page_size=page_size
    )
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    items = [ClientOrderReadBase.model_validate(order) for order in orders]
    return PaginatedResponse(page=page, page_size=page_size, total_items=total_items, total_pages=total_pages, items=items)

def list_all_client_orders_service(
    admin_user_id: int, page: int = 1, page_size: int = 10
) -> PaginatedResponse:
    """(Admin) Lists all client orders"""
    _check_is_admin(admin_user_id) 
    orders, total_items = repo.get_client_orders_paginated(
        client_id=None, page=page, page_size=page_size
    )
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    items = [ClientOrderReadBase.model_validate(order) for order in orders]
    return PaginatedResponse(page=page, page_size=page_size, total_items=total_items, total_pages=total_pages, items=items)

def get_any_client_order_details_service(
    admin_user_id: int, order_id: int
) -> ClientOrderReadDetails:
    """(Admin) Gets any client order details"""
    _check_is_admin(admin_user_id)
    return get_client_order_details_service(user_id=admin_user_id, order_id=order_id, is_admin=True)


def list_all_supplier_orders_service(
    admin_user_id: int, page: int = 1, page_size: int = 10
) -> PaginatedResponse:
    """(Admin) Lists all supplier orders"""
    _check_is_admin(admin_user_id)
    orders, total_items = repo.get_supplier_orders_paginated(page=page, page_size=page_size)
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    items = [SupplierOrderReadBase.model_validate(order) for order in orders]
    return PaginatedResponse(page=page, page_size=page_size, total_items=total_items, total_pages=total_pages, items=items)


def get_supplier_order_details_service(
     admin_user_id: int, order_id: int
) -> SupplierOrderReadDetails:
    """(Admin) Gets supplier order details"""
    _check_is_admin(admin_user_id)
    order = repo.get_supplier_order_by_id(order_id=order_id)
    if not order: raise HTTPException(status_code=404, detail="Supplier order not found")
    return SupplierOrderReadDetails(
        id=order.id, supplier_id=order.supplier_id, product_id=order.product_id,
        amount=order.amount, total_price=order.total_price, status=order.status,
        created_at=order.created_at, updated_at=order.updated_at,
        supplier_name=order.supplier.name if order.supplier else None,
        product_name=order.product.name if order.product else None
    )

def list_custom_client_orders_service(
    admin_user_id: int, page: int = 1, page_size: int = 10
) -> PaginatedResponse:
    """(Admin) Lists custom client orders"""
    _check_is_admin(admin_user_id)
    orders, total_items = repo.get_client_orders_paginated(
        client_id=None, is_custom_price=True, page=page, page_size=page_size
    )
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    items = [ClientOrderReadBase.model_validate(order) for order in orders]
    return PaginatedResponse(page=page, page_size=page_size, total_items=total_items, total_pages=total_pages, items=items)

def get_custom_client_order_details_service(
    admin_user_id: int, order_id: int
) -> ClientOrderReadDetails:
    """(Admin) Gets details of a specific custom client order"""
    _check_is_admin(admin_user_id)
    order_details = get_client_order_details_service(user_id=admin_user_id, order_id=order_id, is_admin=True)
    is_custom = any(p.unit_price == 0 for p in order_details.products)
    if not is_custom: raise HTTPException(status_code=404, detail="Order is not custom")
    return order_details