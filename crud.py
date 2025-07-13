from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from database import session_local, engine
from schemas import *
from models import Base, Product, Taste, Info, Price
from config import get_db

crud_router = APIRouter(
    prefix="/product",
    tags=["Product"]
)


@crud_router.post("/create/", response_model=ProductOut)
def create_full_product(data: ProductCreate, db: Session = Depends(get_db)):
    product = Product(name=data.name)

    for taste_data in data.tastes:
        taste = Taste(taste=taste_data.taste, product=product)

        info = Info(in_stock=taste_data.info.in_stock, taste=taste)

        for price_data in taste_data.info.prices:
            price = Price(volume=price_data.volume, price=price_data.price, info=info)
            db.add(price)

        db.add(info)
        db.add(taste)

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@crud_router.post("/taste/create/", response_model=TasteOut)
def create_taste_with_info(taste_data: TasteCreate, product_name: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(name=product_name).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    taste = Taste(taste=taste_data.taste, product=product)
    info = Info(in_stock=taste_data.info.in_stock, taste=taste)

    for price_data in taste_data.info.prices:
        if not price_data:
            price = Price(volume=price_data.volume, price=price_data.price, info=info)
            db.add(price)
        else:
            raise HTTPException(status_code=404, detail="this taste already exists")
    db.add(taste)
    db.commit()
    db.refresh(taste)

    return taste


@crud_router.patch("/taste/{taste_name}/info")
def update_in_stock(taste_name: str, data: InfoStockUpdate, db: Session = Depends(get_db)):
    taste = db.query(Taste).filter_by(taste=taste_name).first()
    if not taste or not taste.info:
        raise HTTPException(status_code=404, detail="Taste or its info not found")

    taste.info.in_stock = data.in_stock
    db.commit()

    return taste


@crud_router.patch("/price/{product}/{taste}/{volume}")
def update_price(
        product: str,
        taste: str,
        volume: float,
        data: PriceFullUpdate,
        db: Session = Depends(get_db)
):
    product_obj = db.query(Product).filter_by(name=product).first()
    if not product_obj:
        raise HTTPException(status_code=404, detail="Product not found")

    taste_obj = db.query(Taste).filter_by(taste=taste, product_id=product_obj.id).first()
    if not taste_obj:
        raise HTTPException(status_code=404, detail="Taste not found for this product")

    info_obj = db.query(Info).filter_by(taste_id=taste_obj.id).first()
    if not info_obj:
        raise HTTPException(status_code=404, detail="Info not found for this taste")

    price_obj = db.query(Price).filter_by(info_id=info_obj.id, volume=volume).first()
    if not price_obj:
        raise HTTPException(status_code=404, detail="Price with this volume not found")

    if data.volume is not None:
        price_obj.volume = data.volume
    if data.price is not None:
        price_obj.price = data.price

    db.commit()
    return {"message": f"Price for {product}/{taste}/{volume} updated"}


@crud_router.get("/show-all", response_model=List[ProductOut])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@crud_router.delete("/delete/")
def delete_product(
        product_name: str,
        taste_name: Optional[str] = None,
        volume: Optional[float] = None,
        db: Session = Depends(get_db)
):
    product = db.query(Product).filter_by(name=product_name).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Удаление только объёма
    if taste_name and volume is not None:
        taste = db.query(Taste).filter_by(taste=taste_name, product_id=product.id).first()
        if not taste:
            raise HTTPException(status_code=404, detail="Taste not found for this product")

        info = db.query(Info).filter_by(taste_id=taste.id).first()
        if not info:
            raise HTTPException(status_code=404, detail="Info not found")

        price = db.query(Price).filter_by(info_id=info.id, volume=volume).first()
        if not price:
            raise HTTPException(status_code=404, detail="Price with this volume not found")

        db.delete(price)
        db.commit()
        return {"message": f"Deleted price {volume} for taste '{taste_name}' of product '{product_name}'"}

    # Удаление вкуса
    if taste_name:
        taste = db.query(Taste).filter_by(taste=taste_name, product_id=product.id).first()
        if not taste:
            raise HTTPException(status_code=404, detail="Taste not found for this product")

        db.delete(taste)
        db.commit()
        return {"message": f"Deleted taste '{taste_name}' from product '{product_name}'"}

    # Удаление продукта целиком
    db.delete(product)
    db.commit()
    return {"message": f"Deleted product '{product_name}' and all associated data"}
