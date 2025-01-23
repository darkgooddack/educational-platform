### Описание работы OAuth

OAuth производится в два этапа:
1. Получение ссылки для авторизации для обращения к провайдеру
2. Получение токена от провайдера

Далее подробней:
1. Пользователь обращается к эндпоинту /{provider}
(где provider - название OAuth провайдера, например, google, vk, yandex и т.д.)
```python
@router.get("/{provider}", response_class=RedirectResponse)
 async def oauth(
        provider: str,
        ...
```
2. Создаётся экземпляр OAuthService с сессией БД
```python
db_session: AsyncSession = Depends(get_db_session),
```

3. Вызывается get_oauth_url() и сразу проверяется поддерживается ли провайдер
```python
OAuthService(db_session).get_oauth_url(provider)
# где:
if provider not in self.providers:
    raise InvalidProviderError(provider)
```
4. Получается и Валидируется конфигурация провайдера
```python
provider_config = self.providers[provider]
self._validate_provider_config(provider, provider_config)

# где:
required_fields = ["client_id", "client_secret"]
missing = [field for field in required_fields if field not in provider_config]
if missing:
    raise OAuthConfigError(provider, missing)
```
5. Строится URL для авторизации
```python
auth_url = await self._build_auth_url(provider, provider_config)

# где:
params = {
    "client_id": _config["client_id"],
    "redirect_uri": f"{config.app_url}/api/v1/oauth/{provider}/callback",
    "scope": _config.get("scope", ""),
    "response_type": "code",
}

# И для особенностей VK:
if provider == "vk":
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip('=')  # RFC-7636 требует base64url без padding
    params.update({
        "state": secrets.token_urlsafe(32),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "v": "5.131",
    })

    # Сохраняем verifier только для VK
    redis = await RedisClient.get_instance()
    redis.set(f"oauth:verifier:{params['state']}", code_verifier, ex=300)

return f"{_config['auth_url']}?{urlencode(params)}"
```
6. Возвращается редирект
```python
return RedirectResponse(auth_url)
```