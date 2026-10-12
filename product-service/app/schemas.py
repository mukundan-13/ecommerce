
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str = ""
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image_url: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    image_url: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    image_url: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
