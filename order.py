from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db
from models import Product, Taste, Info, Price, Order

from schemas import OrderCreate

order_router = APIRouter(prefix="/orders", tags=["Orders"])


@order_router.post("/")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    created_orders = []

    for item in order.items:
        product = db.query(Product).filter_by(name=item.product_name).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{item.product_name}' not found")

        taste = db.query(Taste).filter_by(product_id=product.id, taste=item.taste).first()
        if not taste:
            raise HTTPException(status_code=404, detail=f"Taste '{item.taste}' not found")

        info = db.query(Info).filter_by(taste_id=taste.id).first()
        if not info or not info.in_stock:
            raise HTTPException(status_code=400, detail=f"'{item.product_name}' with '{item.taste}' is out of stock")

        price = db.query(Price).filter_by(info_id=info.id, volume=item.volume).first()
        if not price:
            raise HTTPException(status_code=404, detail=f"No price found for {item.volume}l")

        new_order = Order(
            customer_name=order.customer_name,
            product_id=product.id,
            taste_id=taste.id,
            price_id=price.id
        )

        db.add(new_order)
        created_orders.append({"product": product.name, "taste": taste.taste, "volume": price.volume, "price": price.price})

    db.commit()

    return {
        "message": f"{len(created_orders)} orders placed for {order.customer_name}",
        "orders": created_orders
    }


@order_router.get("/admin/orders")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    results = []
    for order in orders:
        product = db.query(Product).get(order.product_id)
        taste = db.query(Taste).get(order.taste_id)
        price = db.query(Price).get(order.price_id)

        results.append({
            "order_id": order.id,
            "customer_name": order.customer_name,
            "product": product.name,
            "taste": taste.taste,
            "volume": price.volume,
            "price": price.price
        })

    return results
