from pydantic import BaseModel, Field


class StockCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=0)


class StockResponse(BaseModel):
    product_id: int
    quantity: int


class StockReservation(BaseModel):
    quantity: int = Field(gt=0)
