
from database import engine
from fastapi import FastAPI
import product as products
import variant as variants
import order as orders
import customer as customers
import address as addresses
import order_item as order_items
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
import  auth.auth_routes  as auth_router


app = FastAPI()
app.include_router(products.router)
app.include_router(variants.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(addresses.router)
app.include_router(order_items.router)
# Public routes (like login)
app.include_router(auth_router.router)

#models.Base.metadata.create_all(bind = engine)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

    


