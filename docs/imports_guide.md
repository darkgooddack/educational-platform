# Основные правила импортов

Абсолютные импорты для внешних зависимостей:
```python
import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
```
Абсолютные импорты для базовых модулей приложения:
```python
from app.core.config import config
from app.core.security import HashingMixin, TokenMixin
from app.models import UserModel
from app.schemas import UserCredentialsSchema
```
Относительные импорты для связанных модулей в том же пакете:
```python
from ..users import UserDataManager
from .service import AuthService
```

Группировка импортов по уровням с пустой строкой между группами:
```python
# Стандартная библиотека
import logging
from datetime import datetime

# Внешние зависимости
from fastapi import Depends
from sqlalchemy.orm import Session

# Модули приложения
from app.core.config import config
from app.models import UserModel
from app.schemas import UserCredentialsSchema

# Относительные импорты
from ..users import UserDataManager
```

# Рекомендации

Используй иерархическую структуру импортов:
```
base -> models -> services -> routes
```


Импортируй конкретные модули, а не через init:
```python
from app.services.v1.users import UserService  # Хорошо
from app.services import UserService  # Потенциально опасно
```

Поэтому нужно все импорты переписать :)
Сука, даже не знаю что и делать с этим.

Держи связанные классы в одном модуле:
```python
# users.py
class UserService:
    pass

class UserDataManager:
    pass
```


Используй опережающие объявления типов:
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
```


Разделяй зависимости по уровням:

    core/ - базовые компоненты
    models/ - модели данных
    schemas/ - схемы данных
    services/ - бизнес-логика
    routes/ - эндпоинты

Когда видишь импорт из верхнего уровня в нижний (например, из models в services) - это первый признак потенциальной циклической зависимости.
