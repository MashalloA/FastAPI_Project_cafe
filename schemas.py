from pydantic import BaseModel
from typing import List
from pydantic import BaseModel
from typing import Optional


class PriceCreate(BaseModel):
    volume: float
    price: int


class InfoCreate(BaseModel):
    in_stock: bool
    prices: List[PriceCreate]


class TasteCreate(BaseModel):
    taste: str
    info: InfoCreate


class ProductCreate(BaseModel):
    name: str
    tastes: List[TasteCreate]


class PriceOut(BaseModel):
    id: int
    volume: float
    price: int
    class Config:
        orm_mode = True

class InfoOut(BaseModel):
    in_stock: bool
    prices: List[PriceOut]
    class Config:
        orm_mode = True

class TasteOut(BaseModel):
    id: int
    taste: str
    info: InfoOut
    class Config:
        orm_mode = True

class ProductOut(BaseModel):
    id: int
    name: str
    tastes: List[TasteOut]
    class Config:
        orm_mode = True


class InfoStockUpdate(BaseModel):
    in_stock: bool

class PriceFullUpdate(BaseModel):
    volume: Optional[float] = None
    price: Optional[int] = None