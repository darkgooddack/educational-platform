# Alembic

## Описание

[Alembic](https://alembic.sqlalchemy.org/en/latest/) - это инструмент для управления миграциями базы данных. Он позволяет легко создавать, применять и откатывать изменения в структуре базы данных.

## Использование

- #### Создание новой миграции:

```bash
alembic revision --autogenerate -m "Описание миграции"
```
Эта команда создаст новый файл миграции, который будет содержать изменения, обнаруженные Alembic.

- #### Применение миграции:

```bash
alembic upgrade head # или `uv run migrate`
```
Применяет все миграции до последней версии.


- #### Откат миграции:

```bash
alembic downgrade -1
```
Откатывает последнюю применённую миграцию.


- #### Просмотр истории миграций:

```bash
alembic history
```
Показывает список всех миграций, которые были созданы.


- #### Просмотр текущей миграции:
```bash
alembic current
```
Показывает текущую версию базы данных.

## Важные моменты
- **Значения по умолчанию**: При добавлении нового поля в существующую таблицу, важно указать значение по умолчанию, чтобы избежать ошибок, связанных с NOT NULL ограничениями. Например:
python

```python
op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
```
> Если добавляете новое поле в таблицу, то нужно отредактировать файл миграции и добавить значение по умолчанию для нового поля. Типа `server-default='some_value'`.
Либо нужно просто позаботиться об этом заранее при оформлении модели.

- **Проверка состояния базы данных**: Если Alembic не может определить текущее состояние базы данных, может потребоваться выполнить команду alembic upgrade head, чтобы убедиться, что все миграции применены.

- **Ручное редактирование миграций**: Иногда Alembic может не корректно определить изменения, и вам может потребоваться вручную отредактировать файл миграции, чтобы учесть все изменения, которые вы хотите внести.

- **Тестирование миграций**: Рекомендуется тестировать миграции на локальной или тестовой базе данных перед применением их на продакшене, чтобы избежать потери данных или других проблем.

- **Документирование миграций**: Важно документировать каждую миграцию, чтобы другие разработчики могли понять, что происходит при каждом обновлении базы данных.

## Решение проблем

Ниже можно будет расписывать свои проблемы и их решения.