import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, categories, products, suppliers, orders, search

app = FastAPI()
from fastapi.openapi.utils import get_openapi

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ecomfrontend-production.up.railway.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_time_used(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    duration *= 1000
    print(f"Request to {request.url.path} took {duration:.4f} ms")
    return response


app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(search.router)
app.mount("/static/images/1000x1000", StaticFiles(directory="static/images/1000x1000"), name="images")
app.mount("/static/images/500x500", StaticFiles(directory="static/images/500x500"), name="images")
app.mount("/static/images/100x100", StaticFiles(directory="static/images/100x100"), name="images")
app.mount("/static/images/10x10", StaticFiles(directory="static/images/10x10"), name="images")



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="Your API Description",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "AccessToken": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "`Enter your access token`",
        },
    }

    security_requirements = {
        "/api/auth/logout": ["post"],
        "/api/suppliers/": ["post"],
        "/api/suppliers/{supplier_id}": ["put", "delete"],
        "/api/categories/": ["post"],
        "/api/categories/{category_id}": ["put", "delete"],
        "/api/products/": ["post"],
        "/api/products/{product_id}": ["put", "delete"],
        "/api/orders/": ["post", "get"],
        "/api/orders/my-orders": ["get"],
        "/api/orders/{order_id}": ["put", "delete"],
    }

    for path, methods in security_requirements.items():
        path_item = openapi_schema.get("paths", {}).get(path, {})
        for method in methods:
            if method in path_item:
                operation = path_item[method]
                if "security" not in operation:
                    operation["security"] = [{"AccessToken": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
