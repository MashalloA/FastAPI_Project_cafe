from fastapi import FastAPI
from crud import crud_router
from order import order_router

app = FastAPI()

app.include_router(crud_router)
app.include_router(order_router)