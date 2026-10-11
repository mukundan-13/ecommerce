
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
import models
from routes import router as auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="E-commerce Auth Service",
    lifespan=lifespan,
)
app.include_router(auth_router)

