from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Path,
    status,
    Response,
    Cookie,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database.dto import EmailStr
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
from database.tables import Category, Product, User, Supplier

app = FastAPI()

auth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# DTO


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginFrom(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class SupplierCreate(BaseModel):
    name: str
    contact_email: str
    phone_number: str


class SupplierResponse(BaseModel):
    name: str
    contact_email: str
    phone_number: str


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category_id: int
    supplier_id: int
    quantity: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    quantity: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    category_id: int
    supplier_id: int
    quantity: int

    class Config:
        orm_mode = True


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
