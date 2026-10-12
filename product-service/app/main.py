import os
from contextlib import asynccontextmanager
import time
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine
import models
from dependencies import get_db
from schemas import ProductCreate, ProductUpdate, ProductResponse
from cache import get_cached, set_cached, delete_cached

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")

# Enables the Authorize button in Swagger UI
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError("Missing user ID")

        return {
            "user_id": int(user_id),
            "role": payload.get("role"),
        }

    except (InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="E-commerce Product Service",
    lifespan=lifespan,
)

@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Product).where(
            models.Product.is_active.is_(True)
        )
    ).all()



@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    response: Response,
    db: Session = Depends(get_db),
):
    start_time = time.perf_counter()
    key = f"product:{product_id}"

    # 1. Check Redis
    cached = get_cached(key)

    if cached is not None:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        print(
            f"[REDIS HIT] Product ID: {product_id} | "
            f"Time: {elapsed_ms:.3f} ms"
        )

        response.headers["X-Cache"] = "HIT"
        response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.3f}"
        return cached

    # 2. Cache miss: fetch from PostgreSQL
    product = db.get(models.Product, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    result = ProductResponse.model_validate(product).model_dump(
        mode="json"
    )

    # 3. Save in Redis
    set_cached(key, result)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    print(
        f"[REDIS MISS] Product ID: {product_id} | "
        f"Time: {elapsed_ms:.3f} ms"
    )

    response.headers["X-Cache"] = "MISS"
    response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.3f}"

    return result



@app.patch(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    product = db.get(models.Product, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    delete_cached(f"product:{product_id}")

    return product


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    product = db.get(models.Product, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.is_active = False
    db.commit()
    delete_cached(f"product:{product_id}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
