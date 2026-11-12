# Лабораторна робота №6 — ORM. Вступ до SQLAlchemy. Операції CRUD

### 1. Робота з ORM у Flask Shell

![Команди у Flask Shell](screenshots/flask_shell.png)

---

### 2. Виконання міграцій (Flask-Migrate / Alembic)

![Початкова міграція](screenshots/migration_init.png)

#### 2.2. Оновлення моделі та повторна міграція (`add is_active, author`)

![Оновлення моделі та повторна міграція](screenshots/migration_update.png)

#### 2.3. Структура створеної бази даних (`instance/data.sqlite`)

![Структура таблиці posts](screenshots/db_structure.png)

---

### 3. Інтерфейс користувача та тестування CRUD-операцій

#### 3.1. Відображення списку всіх постів (`GET /post`)

![Список публікацій](screenshots/posts_list.png)

#### 3.2. Додавання нового поста (`GET / POST /post/create`)

![Створення нового поста](screenshots/post_create.png)

#### 3.3. Перегляд окремого поста (`GET /post/<id>`)

![Деталі публікації](screenshots/post_detail.png)

#### 3.4. Редагування поста (`GET / POST /post/<id>/update`)

![Редагування публікації](screenshots/post_edit.png)

#### 3.5. Підтвердження та видалення поста (`GET / POST /post/<id>/delete`)

![Підтвердження видалення](screenshots/post_delete.png)

#### 3.6. Flash-повідомлення після операцій

![Flash повідомлення](screenshots/post_flash.png)

#### 3.7. Обробка помилки 404 (`GET /post/99999`)

![Сторінка 404](screenshots/post_404.png)

---

### 4. Модульні тести

![Результати тестів](screenshots/posts_tests.png)
