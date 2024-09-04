```mermaid 
erDiagram
    USER {
        Integer id
        String username
        String email
        String password_hash
        Boolean is_admin
    }
    ORDER {
        Integer id
        Integer user_id
        DateTime order_date
        String status
    }

    PRODUCT {
        Integer id
        String name
        String description
        Integer price
        DateTime creation_date
        Integer category_id
        Integer supplier_id
        Integer quantity
    }

    CATEGORY {
        Integer id
        String name
        String description
    }

    SUPPLIER {
        Integer id
        String name
        String contact_email
        String phone_number
    }

    ORDER_PRODUCT {
        Integer order_id
        Integer product_id
        Integer quantity
    }
    USER ||--o{ ORDER : places
    ORDER }o--|{ ORDER_PRODUCT : "contains"
    PRODUCT }|--o{ ORDER_PRODUCT : "involves"
    PRODUCT }o--|| CATEGORY : belongs_to
    PRODUCT }o--|| SUPPLIER : supplied_by