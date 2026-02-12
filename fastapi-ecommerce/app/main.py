from fastapi import FastAPI, HTTPException, Query
from fastapi.params import Path
from typing import Optional, List, Dict, Annotated
from pydantic import BaseModel, Field
from service.product import get_all_products



# pydentic validation
class Product(BaseModel):
    id: str
    sku: Annotated[str, Field(min_length=5, max_length=20, title="sku", description="Stock Keeping Unit",example=["SKU12345","375-xyg-9dr5-56tegdf-1524"])]
    name: str



app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI E-commerce Application!"}

# @app.get("/products")
# def get_products():
#     return get_all_products()

@app.get("/products")
def list_products(
    name: str = Query(default=None, min_length=1, max_length=50, description="Filter products by name"),
    sort_by_price: bool = Query(default=False, description="Sort products by price"),
    order: str = Query(default="asc", description="Order of sorting: 'asc' or 'desc'"),
    limit: int = Query(default=10, ge=1, le=100, description="number of products returned"),
    offset: int = Query(default=0, ge=0, description="number of products to skip")
):
    products = get_all_products()


    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    if not products:
        raise HTTPException(status_code=404, detail=f"No products found matching this {name} name.")
    
    if sort_by_price:
        reverse = order.lower() == "desc"
        products = sorted(products, key=lambda p:p.get("price",0), reverse=reverse)


    total = len(products)
    products = products[offset:offset+limit]

    
    return {"total": total, "limit": limit, "items": products}



@app.get("/products/{product_id}")
def get_product_by_id(product_id: str = Path(..., min_length=10, max_length=50, description="UUID of the product to retrieve")):
    products = get_all_products()

    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail=f"product with id {product_id} not found.")



@app.post("/products", status_code=201)
def create_product(product: Product):
    return product