
```mermaid
erDiagram
    UserModel ||--o{ FeedbackModel : manages
    UserModel {
        int id
        string first_name
        string last_name
        string middle_name
        string email
        string phone
        string hashed_password
        UserRole role
        string avatar
        boolean is_active
        int vk_id
        string google_id
        int yandex_id
    }
    FeedbackModel {
        int id
        string name
        string phone
        string email
        FeedbackStatus status
        int manager_id
    }
    UserRole ||--o{ UserModel : has_role
    FeedbackStatus ||--o{ FeedbackModel : has_status
    UserRole {
        string ADMIN
        string MODERATOR
        string USER
        string MANAGER
        string TUTOR
    }
    FeedbackStatus {
        string PENDING
        string PROCESSED
        string DELETED
    }


```
