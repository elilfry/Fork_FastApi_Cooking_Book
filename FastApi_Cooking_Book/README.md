# FastApi_Cooking_Book

Данный проект представляет собой RESTful API для управления базой данных рецептов. Проект написан с использованием фреймворка **FastAPI**, библиотек **SQLAlchemy**, **pydantic** и **Docker**.

Основной функционал:

- CRUD-операции с базой данных;
- Регистрация и авторизация пользователя, разграничение доступа к операциям (Cookies + jwt);
- Фильтрация рецептов по списку ингредиентов;
- Фильтрация рецептов по общему времени приготовления;
- Сортировка рецептов по времени приготовления;
- Парсинг рецептов для заполнения бд через API, с сайта 1000.menu;
- Интеграция с docker-compose, и подъем бд из дампа.

![](docs_image.png)

---
### :hammer_and_wrench: Установка:
- **С Docker, и подъёмом базы данных из дампа:**
1. Поочерёдно выполнить команды: 
```
docker-compose up --build -d  
docker-compose exec db bash 
PGPASSWORD=password pg_restore --verbose --clean --no-acl --no-owner -h db_recipes -U recipes -d recipes dump-recipes.dump
```
2. Ознакомиться с документацией проекта по адресу http://127.0.0.1:8000/docs
#
- **Без Docker, с заполнением таблицы парсингом:**
1. $ pip install -r requirements.txt
2. Установить в файле **.env** актуальное значение переменной DATABASE_URL/ASYNC_DATABASE_URL, и установить localhost в остальны переменные

       - DATABASE_URL = "postgresql://login:password@localhost:5432/db_name"
       - ASYNC_DATABASE_URL = "postgresql+asyncpg://recipes:password@localhost:5432/recipes"
       - POST_URL = "http://localhost:8000/recipes/add_recipe/"
       - LOGIN_URL = "http://localhost:8000/auth/jwt/login"
3) Запустить файл parsing_recipes_for_db.py, дождаться завершения заполнения таблицы
4) Выполнить в консоли команду ```uvicorn main:app --reload```
5) Ознакомиться с документацией проекта по адресу http://127.0.0.1:8000/docs

---
### :bookmark_tabs: Особенности

Опрации создания, редактирования, и удаления рецептов доступны только авторизированным пользователям.
Поэтому, для доступа к выполнению данных операций необходимо пройти процедуру регистрации и авторизации на http://127.0.0.1:8000/docs



#
**Шаблон запроса на добавление рецепта:**
```
{
  "name": "string",
  "description": "string",
  "ingredients": 
  [
    {
      "name": "string",
      "quantity": "string"
    }
  ],
  "steps": 
  [
    {
      "step_description": "string",
      "step_time": int
    }
  ]
}
```
