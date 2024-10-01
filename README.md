### Project Overview

#### How to run

```
cd project/app
docker-compose up -d --build
python seeders.py
```

#### Project Title: **E-Commerce Product Management API**

This project aims to build a RESTful API for managing an e-commerce product catalog. The API will be developed using FastAPI and will interact with a MySQL database deployed via Docker. The API will enable users to perform CRUD operations on products, categories, suppliers, and customer orders. It will also include user authentication using JWT (JSON Web Tokens) to secure certain endpoints.

The project is designed to evaluate the candidate’s ability to write complex SQL queries, especially involving JOINs, and their experience with FastAPI, JWT-based authentication, and handling a MySQL database.

### Requirements

#### 1. **Project Stack:**

- **API Framework:** FastAPI
- **Database:** MySQL (Dockerized)
- **Authentication:** JWT
- **Documentation:** Swagger (integrated with FastAPI)

#### 2. **Database Schema:**

The MySQL database should include at least five tables, with the following suggested structure:

1. **Users** (for storing user details)

- `id` (Primary Key)
- `username`
- `password_hash`
- `email`
- `is_admin` (Boolean to denote admin users)

2. **Products**

- `id` (Primary Key)
- `name`
- `description`
- `price`
- `creation_date` (Timestamp): Automatically set when a new product is added.
- `category_id` (Foreign Key to Categories)
- `supplier_id` (Foreign Key to Suppliers)

3. **Categories**

- `id` (Primary Key)
- `name`
- `description`

4. **Suppliers**

- `id` (Primary Key)
- `name`
- `contact_email`
- `phone_number`

5. **Orders**

- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `product_id` (Foreign Key to Products)
- `quantity`
- `order_date`
- `status` (e.g., Pending, Shipped, Delivered, Cancelled)

#### 3. **Endpoints:**

The API should include the following endpoints:

1. **User Authentication:**

- `POST /auth/login` endpoint should authenticate a user, return a JWT tokens in the response body, and also set the JWT token as a cookie.
- `POST /auth/logout` endpoint that clears the JWT cookies, effectively logging the user out by invalidating the session.
- `POST /auth/register` Registers a new user in the system.

2. **User Management:**

- `GET /users/me`: Retrieve the current user’s details (requires JWT).
- `GET /users/{id}`: Retrieve details of a specific user (Admin only, requires JWT).

3. **Product Management:**

- `GET /products/`: Retrieve a list of products, optionally filtered by category or supplier.
- `GET /products/{id}`: Retrieve details of a specific product.
- `POST /products/`: Create a new product (Admin only, requires JWT).
- `PUT /products/{id}`: Update an existing product (Admin only, requires JWT).
- `DELETE /products/{id}`: Delete a product (Admin only, requires JWT).

4. **Category Management:**

- `GET /categories/`: Retrieve a list of product categories.
- `POST /categories/`: Create a new category (Admin only, requires JWT).

5. **Supplier Management:**

- `GET /suppliers/`: Retrieve a list of suppliers.
- `POST /suppliers/`: Create a new supplier (Admin only, requires JWT).

6. **Order Management:**

- `GET /orders/`: Retrieve a list of orders (Admin only, requires JWT).
- `GET /orders/{id}`: Retrieve details of a specific order (requires JWT).
- `POST /orders/`: Create a new order (requires JWT).
- `PUT /orders/{id}`: Update the status of an order (Admin only, requires JWT).

7. **Search:**

- `GET /search/`:
  Implement an endpoint to search across products, categories, and suppliers using a query parameter. The search functionality should support the following criteria:
  - **Product Name:** Search by product name.
  - **Product Creation Date:** Filter products by their creation date.
  - **Product Price:** Search for products within a specific price range.
  - **Category Name:** Search by the name of the product's category.
  - **Supplier Name:** Search by the name of the supplier.
- **Indexing for Quick Search:**
  To ensure efficient querying, appropriate indexes must be created.

#### 4. **Key Assessment Criteria:**

- Ability to write and optimize complex SQL queries, especially those involving multiple JOINs.
- Proper use of FastAPI to create a RESTful API with well-structured endpoints.
- Implementation of JWT authentication to secure sensitive endpoints.
- Deployment and interaction with a MySQL database using Docker.
- Clear API documentation using Swagger.

```

```
