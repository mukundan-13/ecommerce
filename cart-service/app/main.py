
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine
from models import CartItem
from schemas import (
    CartItemAdd,
    CartItemUpdate,
    CartItemResponse,
)
from security import get_current_user
import os
import grpc

import product_pb2
import product_pb2_grpc

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

PRODUCT_GRPC_HOST = os.getenv("PRODUCT_GRPC_HOST", "localhost:50052")

app = FastAPI(
    title="E-commerce Cart Service",
    lifespan=lifespan,
)


def get_db():
    from database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def verify_product(product_id: int):
    try:
        with grpc.insecure_channel(PRODUCT_GRPC_HOST) as channel:
            client = product_pb2_grpc.ProductServiceStub(channel)

            response = client.GetProduct(
                product_pb2.GetProductRequest(product_id=product_id),
                timeout=3,
            )

            return response

    except grpc.RpcError as error:
        if error.code() == grpc.StatusCode.NOT_FOUND:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail="Product not found or inactive",
            )

        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Product Service is unavailable",
        )
    
@app.get("/cart", response_model=list[CartItemResponse])
def get_cart(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(CartItem).where(CartItem.user_id == user_id)
    ).all()

@app.post(
    "/cart/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_cart(
    payload: CartItemAdd,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Verify product through Product Service gRPC
    verify_product(payload.product_id)

    # 2. Check whether the item already exists in this user's cart
    item = db.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == payload.product_id,
        )
    )

    # 3. Increment quantity or create a new item
    if item:
        item.quantity += payload.quantity
    else:
        item = CartItem(
            user_id=user_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(item)

    # 4. Save changes
    db.commit()
    db.refresh(item)

    return item



@app.patch(
    "/cart/items/{product_id}",
    response_model=CartItemResponse,
)
def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)
    return item


@app.delete(
    "/cart/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_cart_item(
    product_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    db.delete(item)
    db.commit()
