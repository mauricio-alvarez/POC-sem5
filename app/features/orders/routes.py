from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from typing import List, Optional

from app.core.database import get_session
from .models import OrderStatus
from .schemas import (
    ClientOrderPurchaseRequest, ClientOrderCustomRequest, OrderCreateResponse,
    ClientOrderReadBase, ClientOrderReadDetails, PaginatedResponse,
    SupplierOrderReadBase, SupplierOrderReadDetails
)
from .services import (
    create_purchase_order_service, create_custom_order_service,
    get_client_order_details_service, list_client_orders_service,
    list_all_client_orders_service, get_any_client_order_details_service,
    list_all_supplier_orders_service, get_supplier_order_details_service,
    list_custom_client_orders_service, get_custom_client_order_details_service
)

router = APIRouter(prefix="/order", tags=["orders"], dependencies=[Depends(get_session)])
# All
@router.get("/all", response_model=PaginatedResponse, summary="List User's Orders")
async def get_my_orders(
    id_user: int = Query(..., description="ID of the user requesting their orders"),
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100, alias="limit"),
    state: Optional[OrderStatus] = Query(None)
):
    try:
        # Service does not need session passed
        return list_client_orders_service(user_id=id_user, page=page, page_size=page_size, state=state)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# By id
@router.get("/{order_id}", response_model=ClientOrderReadDetails, summary="Get User's Order Details")
async def get_my_order_details(order_id: int = Path(..., ge=1), id_user: int = Query(...)):
    try:
        # Service does not need session passed
        return get_client_order_details_service(user_id=id_user, order_id=order_id)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Post Custom Order
@router.post("/custom", response_model=OrderCreateResponse, status_code=201, summary="Create Custom Order")
async def create_custom_order(custom_data: ClientOrderCustomRequest = Body(...), id_user: int = Query(...)):
    try:
        # Service does not need session passed
        return create_custom_order_service(user_id=id_user, custom_data=custom_data)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Post Purchase Order
@router.post("/purchase", response_model=OrderCreateResponse, status_code=201, summary="Create Purchase Order")
async def create_purchase_order(order_data: ClientOrderPurchaseRequest = Body(...), id_user: int = Query(...)):
    try:
        # Service does not need session passed
        return create_purchase_order_service(user_id=id_user, order_data=order_data)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Admin view All
@router.get("/purchases/all", response_model=PaginatedResponse, summary="[Admin] List Client Orders", tags=["admin"])
async def admin_get_all_client_orders(id_user: int = Query(...), page: int = Query(1), page_size: int = Query(10, alias="limit")):
    try:
        return list_all_client_orders_service(admin_user_id=id_user, page=page, page_size=page_size)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Admin view by id
@router.get("/purchases/{order_id}", response_model=ClientOrderReadDetails, summary="[Admin] Get Client Order", tags=["admin"])
async def admin_get_client_order_details(order_id: int = Path(..., ge=1), id_user: int = Query(...)):
    try:
        return get_any_client_order_details_service(admin_user_id=id_user, order_id=order_id)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Admin view all Supplier Orders
@router.get("/sales/all", response_model=PaginatedResponse, summary="[Admin] List Supplier Orders", tags=["admin"])
async def admin_get_all_supplier_orders(id_user: int = Query(...), page: int = Query(1), page_size: int = Query(10, alias="limit")):
    try:
        return list_all_supplier_orders_service(admin_user_id=id_user, page=page, page_size=page_size)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Admin view Supplier Orders by id
@router.get("/sales/{order_id}", response_model=SupplierOrderReadDetails, summary="[Admin] Get Supplier Order", tags=["admin"])
async def admin_get_supplier_order_details(order_id: int = Path(..., ge=1), id_user: int = Query(...)):
    try:
        return get_supplier_order_details_service(admin_user_id=id_user, order_id=order_id)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Admin view Custom Orders
@router.get("/custom/all", response_model=PaginatedResponse, summary="[Admin] List Custom Orders", tags=["admin"])
async def admin_get_all_custom_orders(id_user: int = Query(...), page: int = Query(1), page_size: int = Query(10, alias="limit")):
    try:
        return list_custom_client_orders_service(admin_user_id=id_user, page=page, page_size=page_size)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")

# Admin view Custom Order by id
@router.get("/custom/{order_id}", response_model=ClientOrderReadDetails, summary="[Admin] Get Custom Order", tags=["admin"])
async def admin_get_custom_order_details(order_id: int = Path(..., ge=1), id_user: int = Query(...)):
    try:
        return get_custom_client_order_details_service(admin_user_id=id_user, order_id=order_id)
    except HTTPException as e: raise e
    except Exception as e: print(f"Error: {e}"); raise HTTPException(500, "Internal server error")