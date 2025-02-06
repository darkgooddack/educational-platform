# Class diagrams
```mermaid
classDiagram
    class BaseOAuthProvider {
        <<Абстрактный>>
        -logger
        -provider: OAuthProvider
        -config: OAuthConfig
        -user_handler
        -auth_service: AuthService
        -user_service: UserService
        -redis_storage: OAuthRedisStorage
        -http_client: OAuthHttpClient
        +authenticate(user_data)
        +get_auth_url()*
        +get_token(code, state)*
        +get_user_info(token)*
        -_get_callback_url()*
        -_handle_state(state, token_params)*
        -_validate_config()
        -_find_user(user_data)
        -_create_user(user_data)
        -_create_tokens(user)
    }

    class VKOAuthProvider {
        +get_auth_url()
        +get_token(code, state)
        +get_user_info(token)
        -_get_callback_url()
        -_handle_state(state, token_params)
        -_generate_code_challenge(verifier)
        -_get_email(user_data)
    }

    class GoogleOAuthProvider {
        +get_auth_url()
        +get_token(code, state) 
        +get_user_info(token)
        -_get_callback_url()
        -_handle_state(state, token_params)
        -_get_provider_id(user_data)
    }

    class YandexOAuthProvider {
        +get_auth_url()
        +get_token(code, state)
        +get_user_info(token)
        -_get_callback_url()
        -_handle_state(state, token_params)
        -_get_email(user_data)
    }

    class OAuthService {
        -PROVIDERS
        -session: AsyncSession
        -logger
        +get_provider(provider)
        +get_oauth_url(provider)
        +authenticate(provider, code)
    }

    BaseOAuthProvider <|-- VKOAuthProvider
    BaseOAuthProvider <|-- GoogleOAuthProvider 
    BaseOAuthProvider <|-- YandexOAuthProvider
    OAuthService --> BaseOAuthProvider

    note for VKOAuthProvider "Проблема: несоответствие state/verifier
    1. get_auth_url() генерирует code_verifier
    2. state передается некорректно
    3. _handle_state() не находит verifier"
```
# Sequence diagrams
```mermaid
sequenceDiagram
    participant User
    participant App
    participant VK as VK (id.vk.com)
    participant Redis

    %% VK OAuth Flow
    User->>App: GET /api/v1/oauth/vk
    App->>Redis: Сохраняем code_verifier
    App->>VK: GET https://id.vk.com/authorize
    Note over App,VK: code_challenge + state
    VK->>App: Редирект на callback_url
    App->>Redis: Получаем code_verifier
    App->>VK: POST https://id.vk.com/oauth2/auth
    Note over App,VK: code + code_verifier
    VK->>App: access_token
    App->>VK: GET https://id.vk.com/oauth2/user_info
    VK->>App: user_data
    App->>User: JWT + redirect

    %% Google Flow
    participant Google as Google (accounts.google.com)
    User->>App: GET /api/v1/oauth/google
    App->>Google: GET https://accounts.google.com/o/oauth2/v2/auth
    Note over App,Google: scope: email profile
    Google->>App: Редирект на callback_url
    App->>Google: POST https://oauth2.googleapis.com/token
    Google->>App: access_token + id_token
    App->>Google: GET https://www.googleapis.com/oauth2/v2/userinfo
    Google->>App: user_data
    App->>User: JWT + redirect

    %% Yandex Flow
    participant Yandex as Yandex (oauth.yandex.ru)
    User->>App: GET /api/v1/oauth/yandex
    App->>Yandex: GET https://oauth.yandex.ru/authorize
    Note over App,Yandex: scope: login:email
    Yandex->>App: Редирект на callback_url
    App->>Yandex: POST https://oauth.yandex.ru/token
    Yandex->>App: access_token
    App->>Yandex: GET https://login.yandex.ru/info
    Yandex->>App: user_data
    App->>User: JWT + redirect
```

```marmaid
sequenceDiagram
    participant User
    participant App
    participant Redis
    participant VK as VK (id.vk.com)

    %% Initial Auth Request
    User->>App: GET /api/v1/oauth/vk
    Note over App: generate code_verifier & state
    App->>Redis: SET vk_verifier_{state}=code_verifier (300s)
    Note over App: generate code_challenge (S256)
    App->>VK: GET /authorize
    Note over App,VK: client_id, redirect_uri, scope,<br/>state, code_challenge, code_challenge_method

    %% Auth Response & Token Exchange
    VK->>App: Redirect to callback_url
    Note over VK,App: code, state, device_id
    App->>Redis: GET vk_verifier_{state}
    App->>Redis: DELETE vk_verifier_{state}
    App->>VK: POST /oauth2/auth
    Note over App,VK: client_id, client_secret, code,<br/>redirect_uri, code_verifier, device_id

    %% Token Response & User Info
    VK-->>App: {access_token, token_type, expires_in}
    App->>VK: GET /oauth2/user_info
    Note over VK,App: Authorization: Bearer {token}
    VK-->>App: {email, id, first_name, last_name}
    App->>User: JWT + redirect

```
```mermaid
sequenceDiagram
    participant User
    participant App
    participant Redis
    participant VK as VK (id.vk.com)

    User->>App: GET /api/v1/oauth/vk
    App->>Redis: Сохраняем code_verifier
    App->>VK: GET https://id.vk.com/authorize
    Note over App,VK: code_challenge + state
    VK->>App: Редирект на callback_url
    Note over VK,App: code, state, device_id
    App->>Redis: Получаем code_verifier
    App->>Redis: Удаляем code_verifier
    App->>VK: POST https://id.vk.com/oauth2/auth
    Note over App,VK: client_id, client_secret, code,<br/>redirect_uri, code_verifier, device_id
    VK-->>App: {access_token, token_type, expires_in}
    App->>VK: GET https://id.vk.com/oauth2/user_info
    Note over VK,App: Authorization: Bearer {token}
    VK-->>App: {email, id, first_name, last_name}
    App->>User: JWT + redirect
```