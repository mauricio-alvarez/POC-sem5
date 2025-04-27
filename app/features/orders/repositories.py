from sqlmodel import select, func, Session
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Tuple
import math

from app.core.database import db_session
from .models import (
    ClientOrder, ClientOrderProduct, OrderStatus, SupplierOrder
)
from app.features.auth.models import User, Role
from app.features.products.models import Product
from app.features.suppliers.models import Supplier
from app.features.products.repositories import create_product as create_product_repo_ext
from app.features.products.repositories import get_product as get_product_repo_ext


def get_user_with_roles(user_id: int) -> Optional[User]:
    """Fetches a user and eagerly loads their roles."""
    session: Session = db_session.get() 
    statement = select(User).where(User.id == user_id).options(selectinload(User.roles))
    return session.exec(statement).first()

def get_products_by_ids(product_ids: List[int]) -> List[Product]:
    """Gets multiple products by their IDs."""
    session: Session = db_session.get() 
    if not product_ids:
        return []
    statement = select(Product).where(Product.id.in_(product_ids))
    return session.exec(statement).all()

def create_product(product: Product) -> None:
    """Creates a new product. Matches product repo style."""
    session: Session = db_session.get() 
    session.add(product)
    session.commit()

def get_product(product_id: int) -> Optional[Product]:
    """Gets a product by ID."""
    session: Session = db_session.get() 
    return session.get(Product, product_id) 

def update_product_stock(product_id: int, amount_to_decrease: int) -> bool:
    """ Decreases stock. Commits immediately. Returns True on success. """
    session: Session = db_session.get() 
    product = session.get(Product, product_id)
    if product and product.stock >= amount_to_decrease:
        product.stock -= amount_to_decrease
        session.add(product)
        session.commit() 
        return True
    return False 

def create_client_order(order: ClientOrder) -> ClientOrder:
    """Creates a new client order. Commits immediately."""
    session: Session = db_session.get() 
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def add_product_to_client_order(order_id: int, product_id: int, amount: int, unit_price: float) -> ClientOrderProduct:
    """Adds a product link to a client order. Commits immediately."""
    session: Session = db_session.get() 
    link = ClientOrderProduct(
        order_id=order_id,
        product_id=product_id,
        amount=amount,
        unit_price=unit_price
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

def get_client_order_by_id(
    order_id: int,
    client_id: Optional[int] = None,
    is_admin: bool = False
) -> Optional[ClientOrder]:
    """Gets a specific client order by ID."""
    session: Session = db_session.get() 
    statement = select(ClientOrder).where(ClientOrder.id == order_id)
    if not is_admin and client_id is not None:
        statement = statement.where(ClientOrder.client_id == client_id)
    statement = statement.options(
        selectinload(ClientOrder.product_links).joinedload(ClientOrderProduct.product)
    )
    return session.exec(statement).first()

def get_client_orders_paginated(
    client_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    is_custom_price: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10
) -> Tuple[List[ClientOrder], int]:
    """Gets a paginated list of client orders with optional filters."""
    session: Session = db_session.get() 
    offset = (page - 1) * page_size
    statement = select(ClientOrder)
    count_statement = select(func.count(ClientOrder.id)) 
    
    filters = []
    count_filters = []
    if client_id is not None:
        filters.append(ClientOrder.client_id == client_id)
        count_filters.append(ClientOrder.client_id == client_id)
    if status:
        filters.append(ClientOrder.status == status)
        count_filters.append(ClientOrder.status == status)

    base_query_joins = False
    if is_custom_price is not None:
        base_query_joins = True
        statement = statement.join(ClientOrderProduct).join(Product)
        if is_custom_price:
             filters.append(Product.price == 0)
        statement = statement.distinct() 

    if filters:
        statement = statement.where(*filters)

    if is_custom_price is not None or count_filters:
        count_statement = select(func.count(ClientOrder.id.distinct())).select_from(ClientOrder)
        if count_filters:
             count_statement = count_statement.where(*count_filters)
        if is_custom_price is not None:
             count_statement = count_statement.join(ClientOrderProduct).join(Product)
             if is_custom_price:
                  count_statement = count_statement.where(Product.price == 0)


    total_items = session.exec(count_statement).one_or_none() or 0

    orders = session.exec(
        statement.order_by(ClientOrder.created_at.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    return orders, total_items


def get_supplier_order_by_id(order_id: int) -> Optional[SupplierOrder]:
    """Gets a specific supplier order by ID."""
    session: Session = db_session.get() 
    statement = select(SupplierOrder).where(SupplierOrder.id == order_id)
    statement = statement.options(
        joinedload(SupplierOrder.product),
        joinedload(SupplierOrder.supplier)
    )
    return session.exec(statement).first()

def get_supplier_orders_paginated(
    page: int = 1,
    page_size: int = 10
) -> Tuple[List[SupplierOrder], int]:
    """Gets a paginated list of all supplier orders."""
    session: Session = db_session.get() 
    offset = (page - 1) * page_size
    count_statement = select(func.count()).select_from(SupplierOrder)
    total_items = session.exec(count_statement).one()

    statement = select(SupplierOrder) \
        .order_by(SupplierOrder.created_at.desc()) \
        .offset(offset) \
        .limit(page_size) \
        .options(
            joinedload(SupplierOrder.product),
            joinedload(SupplierOrder.supplier)
        )
    orders = session.exec(statement).all()
    return orders, total_items