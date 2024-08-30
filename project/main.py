from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Path,
    status,
    Response,
    Cookie,
    Query,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from database.tables import order_product_table
from database.dto import (
    CategoryCreate,
    CategoryResponse,
    OrderCreate,
    OrderProductResponse,
    OrderResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    SupplierCreate,
    SupplierResponse,
    TokenResponse,
    UserCreate,
)
from jwt_token import (
    get_user_by_token,
    verify_refresh_token,
    create_access_token,
    create_refresh_token,
    set_jwt_cookie,
    remove_jwt_cookie,
)
from utils import (
    verify_password,
    get_user_by_email,
    hash_password,
)
from database.database import get_db, get_root_db
from database.tables import Category, Order, Product, User, Supplier

app = FastAPI()

auth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# auth


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    response: Response = Response(),
):
    user = get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )

    set_jwt_cookie(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token_auth(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db),
    token: str = Depends(auth2_scheme),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        token_data = verify_refresh_token(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(
        data={"sub": token_data["sub"], "user_id": token_data["user_id"]}
    )
    set_jwt_cookie(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@app.post(
    "/auth/logout",
    summary="Logout User",
    response_description="Successfully logged out",
)
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    token: str = Depends(auth2_scheme),
):
    remove_jwt_cookie(response)
    return {"msg": "Successfully logged out"}


@app.post("/auth/register", response_model=UserCreate)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User).filter(User.email == user_data.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserCreate(
        username=new_user.username,
        email=new_user.email,
        password=user_data.password,
    )


# suppliers


@app.post("/suppliers", response_model=SupplierCreate)
async def create_supplier_admin_only(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_root_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    existing_supplier = (
        db.query(Supplier)
        .filter(Supplier.contact_email == supplier_data.contact_email)
        .first()
    )
    if existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier with this email already exists",
        )

    new_supplier = Supplier(
        name=supplier_data.name,
        contact_email=supplier_data.contact_email,
        phone_number=supplier_data.phone_number,
    )

    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return SupplierCreate(
        name=new_supplier.name,
        contact_email=new_supplier.contact_email,
        phone_number=new_supplier.phone_number,
    )


@app.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).all()
    if not suppliers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No suppliers found"
        )
    return suppliers


# categories


@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No categories found"
        )
    return categories


@app.post("/categories", response_model=CategoryResponse)
async def create_category_admin_only(
    category_data: CategoryCreate,
    db: Session = Depends(get_root_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    existing_category = (
        db.query(Category).filter(Category.name == category_data.name).first()
    )
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )

    new_category = Category(
        name=category_data.name,
        description=category_data.description,
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return CategoryResponse(
        id=new_category.id,
        name=new_category.name,
        description=new_category.description,
    )


# products


@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)

    products = query.all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No products found"
        )
    return products


@app.get("/products/{id}", response_model=ProductResponse)
async def get_product(
    id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@app.post("/products", response_model=ProductResponse)
async def create_product_admin_only(
    product_data: ProductCreate,
    db: Session = Depends(get_root_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    existing_product = (
        db.query(Product).filter(Product.name == product_data.name).first()
    )
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists",
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
        supplier_id=product_data.supplier_id,
        quantity=product_data.quantity,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        description=new_product.description,
        price=new_product.price,
        category_id=new_product.category_id,
        supplier_id=new_product.supplier_id,
        quantity=new_product.quantity,
    )


@app.put("/products/{id}", response_model=ProductResponse)
async def update_product_admin_only(
    product_data: ProductUpdate,
    id: int = Path(..., gt=0),
    db: Session = Depends(get_root_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    for key, value in product_data.dict().items():
        if value is not None:
            setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        supplier_id=product.supplier_id,
        quantity=product.quantity,
    )


@app.delete("/products/{id}", response_description="Product deleted")
async def delete_product_admin_only(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_root_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"msg": "Product deleted"}


# Orders


@app.get("/orders", response_model=List[OrderResponse])
async def get_orders_admin_only(
    db: Session = Depends(get_root_db), token: str = Depends(auth2_scheme)
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    orders = db.query(Order).all()
    order_responses = []
    for order in orders:
        products_with_quantity = []
        for product in order.products:
            quantity = (
                db.query(order_product_table)
                .filter_by(order_id=order.id, product_id=product.id)
                .first()
                .quantity
            )
            products_with_quantity.append(
                OrderProductResponse(
                    product_id=product.id,
                    name=product.name,
                    quantity=quantity,
                )
            )

        order_responses.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                order_date=order.order_date.isoformat(),
                status=order.status,
                products=products_with_quantity,
            )
        )

    return order_responses


@app.get("/orders/{id}", response_model=OrderResponse)
async def get_order(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)
    order = db.query(Order).filter(Order.id == id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order",
        )

    order_products = (
        db.query(
            order_product_table.c.product_id, order_product_table.c.quantity
        )
        .filter(order_product_table.c.order_id == id)
        .all()
    )

    product_quantities = {
        product_id: quantity for product_id, quantity in order_products
    }

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        order_date=order.order_date.isoformat(),
        status=order.status,
        products=[
            OrderProductResponse(
                product_id=product.id,
                name=product.name,
                quantity=product_quantities.get(product.id, 0),
            )
            for product in order.products
        ],
    )


@app.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    new_order = Order(user_id=user.id)

    db.add(new_order)
    db.commit()

    for item in order_data.products:
        product = (
            db.query(Product).filter(Product.id == item.product_id).first()
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )
        order_product_entry = order_product_table.insert().values(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
        )
        db.execute(order_product_entry)

    db.commit()

    db.refresh(new_order)

    return OrderResponse(
        id=new_order.id,
        user_id=new_order.user_id,
        order_date=new_order.order_date.isoformat(),
        status=new_order.status,
        products=[
            OrderProductResponse(
                product_id=product.id,
                name=product.name,
                quantity=item.quantity,
            )
            for product in new_order.products
        ],
    )


@app.put("/orders/{id}", response_model=OrderResponse)
async def update_order_status(
    id: int,
    status: str,
    db: Session = Depends(get_root_db),
    token: str = Depends(auth2_scheme),
):
    user = get_user_by_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    order = db.query(Order).filter(Order.id == id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    order.status = status
    db.commit()
    db.refresh(order)

    order_products = (
        db.query(
            order_product_table.c.product_id, order_product_table.c.quantity
        )
        .filter(order_product_table.c.order_id == id)
        .all()
    )

    product_quantities = {
        product_id: quantity for product_id, quantity in order_products
    }

    products = (
        db.query(Product)
        .filter(Product.id.in_(product_quantities.keys()))
        .all()
    )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        order_date=order.order_date.isoformat(),
        status=order.status,
        products=[
            OrderProductResponse(
                product_id=product.id,
                name=product.name,
                quantity=product_quantities.get(product.id, 0),
            )
            for product in products
        ],
    )


# search


@app.get("/search/", response_model=List[ProductResponse])
async def search_products(
    product_name: Optional[str] = Query(
        None, description="Search by product name"
    ),
    creation_date_from: Optional[str] = Query(
        None, description="Filter products created after this date"
    ),
    creation_date_to: Optional[str] = Query(
        None, description="Filter products created before this date"
    ),
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    category_name: Optional[str] = Query(
        None, description="Search by category name"
    ),
    supplier_name: Optional[str] = Query(
        None, description="Search by supplier name"
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if product_name:
        query = query.filter(Product.name.ilike(f"%{product_name}%"))

    if creation_date_from:
        query = query.filter(Product.creation_date >= creation_date_from)

    if creation_date_to:
        query = query.filter(Product.creation_date <= creation_date_to)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if category_name:
        query = query.join(Category).filter(
            Category.name.ilike(f"%{category_name}%")
        )

    if supplier_name:
        query = query.join(Supplier).filter(
            Supplier.name.ilike(f"%{supplier_name}%")
        )

    products = query.all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found matching the criteria",
        )

    return products
