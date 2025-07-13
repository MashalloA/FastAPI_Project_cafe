from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from models import Product, Taste, Price
from routers.order import order_router
from routers.crud import crud_router
from config import get_db
from routers.order import get_all_orders

app = FastAPI()

app.include_router(order_router)
app.include_router(crud_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/order", response_class=HTMLResponse)
def order_form(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product.name).distinct().all()
    tastes = db.query(Taste.taste).distinct().all()
    volumes = db.query(Price.volume).distinct().order_by(Price.volume).all()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": [p.name for p in products],
        "tastes": [t.taste for t in tastes],
        "volumes": [v.volume for v in volumes]
    })


@app.get("/admin/orders", response_class=HTMLResponse)
def admin_orders(request: Request, db: Session = Depends(get_db)):
    orders = get_all_orders(db)
    return templates.TemplateResponse("admin_orders.html", {
        "request": request,
        "orders": orders
    })

@app.get("/manage", response_class=HTMLResponse)
def manage_products(request: Request):
    return templates.TemplateResponse("manage_products.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})
