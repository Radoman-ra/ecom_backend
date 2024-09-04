from fastapi import FastAPI

from routers import auth, categories, products, suppliers, orders, search

app = FastAPI()
from fastapi.openapi.utils import get_openapi

app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(search.router)


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
        "/auth/logout": ["post"],
        "/suppliers": ["post"],
        "/categories": ["post"],
        "/products": ["post"],
        "/products/{id}": ["put", "delete"],
        "/orders": ["post", "get"],
        "/orders/{id}": ["put"],
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
