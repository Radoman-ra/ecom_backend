<details>
    <summary>Progress</summary>

<details>
<summary>ver noname</summary>

- Set up project
- Set up database
- Empty database, bridge, and Docker files are ready
- Develop `models/users.py` and `dto/users.py`
- Work on roadmap, database, and DTOs, `dto/users.py`  now is `dto.py`

</details>
<details>
<summary>ver noname2</summary>

- Authentication
- Databases 
</details>
<details>
<summary>16 August</summary>

- Rewrigt databases
- 
</details>
</details>
<details>
  <summary>TO DO</summary>

</details>

### Roadmap for E-Commerce Product Management API

<details>
  <summary>Phase 1: Planning and Setup</summary>

  1. **Requirements Gathering and Planning**
     - Finalize API requirements and endpoints.
     - Define the database schema and relationships in detail.
     - Prepare a detailed project plan, including timelines and milestones.

  2. **Environment Setup**
     - Install Docker and Docker Compose.
     - Set up MySQL Docker container with initial configurations.
     - Set up a Python virtual environment for FastAPI development.
     - Install necessary libraries: FastAPI, SQLAlchemy (or other ORM), Pydantic, PyJWT, etc.

  3. **Database Design**
     - Design the database schema based on the requirements.
     - Write SQL scripts to create tables with relationships.
     - Initialize the database with sample data.

</details>

<details>
  <summary>Phase 2: Development</summary>

  4. **API Structure and FastAPI Setup**
     - Create the initial FastAPI project structure.
     - Set up basic routing and configuration.
     - Configure database connections and models using an ORM (e.g., SQLAlchemy).

  5. **User Authentication**
     - Implement JWT-based authentication:
       - `/auth/login` for user authentication and JWT issuance.
       - `/auth/logout` for invalidating JWT sessions.
     - Set up user registration and password hashing.

  6. **User Management Endpoints**
     - Implement user creation (`POST /users`).
     - Implement user details retrieval (`GET /users/me`, `GET /users/{id}`).
     - Implement user role checks (e.g., Admin) for restricted endpoints.

  7. **Product Management Endpoints**
     - Implement product listing (`GET /products`), detail retrieval (`GET /products/{id}`).
     - Implement product creation (`POST /products`), update (`PUT /products/{id}`), and deletion (`DELETE /products/{id}`).

  8. **Category Management Endpoints**
     - Implement category listing (`GET /categories`).
     - Implement category creation (`POST /categories`).

  9. **Supplier Management Endpoints**
     - Implement supplier listing (`GET /suppliers`).
     - Implement supplier creation (`POST /suppliers`).

  10. **Order Management Endpoints**
      - Implement order listing (`GET /orders`), detail retrieval (`GET /orders/{id}`).
      - Implement order creation (`POST /orders`), and status update (`PUT /orders/{id}`).

  11. **Search Functionality**
      - Implement the `/search/` endpoint to support querying across products, categories, and suppliers.

  12. **Indexing and Performance Optimization**
      - Create indexes on frequently queried fields to optimize performance.
      - Implement query optimization techniques where necessary.

</details>

<details>
  <summary>Phase 3: Testing</summary>

  13. **Unit and Integration Testing**
      - Write unit tests for individual components and functions.
      - Write integration tests to verify end-to-end functionality of the API.

  14. **API Testing**
      - Test all endpoints for correctness, security, and performance.
      - Use tools like Postman or Swagger UI for manual testing.

  15. **Security Testing**
      - Test JWT authentication and authorization mechanisms.
      - Verify that sensitive endpoints are properly secured.

</details>

<details>
  <summary>Phase 4: Documentation and Deployment</summary>

  16. **API Documentation**
      - Ensure Swagger documentation is accurate and up-to-date.
      - Include descriptions for all endpoints, request/response models, and authentication methods.

  17. **Containerization and Deployment**
      - Create Dockerfile and Docker Compose configuration for deploying the FastAPI application.
      - Deploy the application and database containers.
      - Set up environment variables and configuration files for production.

  18. **Monitoring and Maintenance**
      - Set up monitoring tools to track application performance and errors.
      - Plan for ongoing maintenance, including updates and bug fixes.

</details>

<details>
  <summary>Phase 5: Review and Handoff</summary>

  19. **Code Review**
      - Conduct code reviews to ensure code quality and adherence to best practices.
      - Incorporate feedback and make necessary adjustments.

  20. **Final Testing and Validation**
      - Perform final testing to ensure everything is functioning as expected.
      - Validate deployment in a staging environment before production.

  21. **Handoff and Documentation**
      - Provide documentation and support materials for deployment and maintenance.
      - Handoff the project to the relevant team or individual.

</details>
