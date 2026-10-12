from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Inventory
from schemas import StockCreate, StockResponse, StockReservation
from security import get_current_user, require_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="E-commerce Inventory Service",
    lifespan=lifespan,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/inventory/{product_id}",
    response_model=StockResponse,
)
def get_stock(
    product_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stock = db.get(Inventory, product_id)

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found",
        )

    return stock


@app.post(
    "/inventory",
    response_model=StockResponse,
    status_code=201,
)
def create_stock(
    payload: StockCreate,
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.get(Inventory, payload.product_id)

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Inventory record already exists",
        )

    stock = Inventory(
        product_id=payload.product_id,
        quantity=payload.quantity,
    )

    db.add(stock)
    db.commit()
    db.refresh(stock)

    return stock


@app.post("/inventory/{product_id}/reserve")
def reserve_stock(
    product_id: int,
    payload: StockReservation,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = db.execute(
            update(Inventory)
            .where(
                Inventory.product_id == product_id,
                Inventory.quantity >= payload.quantity,
            )
            .values(
                quantity=Inventory.quantity - payload.quantity
            )
        )

        if result.rowcount == 0:
            db.rollback()

            exists = db.get(Inventory, product_id)

            if exists is None:
                raise HTTPException(
                    status_code=404,
                    detail="Inventory record not found",
                )

            raise HTTPException(
                status_code=409,
                detail="Insufficient stock",
            )

        db.commit()

        return {
            "message": "Stock reserved successfully",
            "product_id": product_id,
            "reserved_quantity": payload.quantity,
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to reserve stock",
        )