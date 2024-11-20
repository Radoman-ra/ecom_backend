import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, categories, products, suppliers, orders, search, profile

app = FastAPI()
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

origins = [
    os.getenv("FRONTEND_URL"),
    os.getenv("FRONTEND_URL_2")
]
print(os.getenv("FRONTEND_URL"))
print(os.getenv("FRONTEND_URL_2"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "default_secret"),
)

@app.middleware("http")
async def log_time_used(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    duration *= 1000
    print(f"Request to {request.url.path} took {duration:.4f} ms")
    return response

directories = [
    "static/avatars",
    "static/images/10x10",
    "static/images/100x100",
    "static/images/500x500",
    "static/images/1000x1000",
]

for directory in directories:
    path = Path(directory)
    if not path.exists():
        path.mkdir(parents=True)
        
app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(search.router)
app.include_router(profile.router)
app.mount("/static", StaticFiles(directory="static"), name="images")


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
