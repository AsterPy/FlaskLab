import unittest
from sqlalchemy import select
from app import create_app, db, bcrypt
from app.users.models import User


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування тестового додатку та in-memory БД."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Очищення БД після кожного тесту."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 1. Views Tests: коректне завантаження сторінок реєстрації та входу
    def test_register_page_loads(self):
        """GET /users/register повертає 200 і містить поля форми реєстрації."""
        response = self.client.get("/users/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username", response.data)
        self.assertIn(b"Email", response.data)
        self.assertIn(b"Password", response.data)
        self.assertIn(b"Confirm Password", response.data)

    def test_login_page_loads(self):
        """GET /users/login повертає 200 і містить поля форми входу."""
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email", response.data)
        self.assertIn(b"Password", response.data)
        self.assertIn(b"Remember Me", response.data)

    # 2. Тестування збереження користувача у БД при реєстрації
    def test_user_registration_saves_hashed_password(self):
        """POST /users/register зберігає нового користувача в БД з хешованим паролем."""
        response = self.client.post(
            "/users/register",
            data={
                "username": "testuser1",
                "email": "testuser1@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Account created for testuser1!", response.data)

        user = db.session.scalar(select(User).where(User.email == "testuser1@example.com"))
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser1")
        self.assertNotEqual(user.password, "password123")
        self.assertTrue(bcrypt.check_password_hash(user.password, "password123"))
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.check_password("wrongpass"))

    def test_registration_duplicate_username_and_email(self):
        """Реєстрація з існуючим username або email відхиляється валідаторами."""
        existing = User(username="existing1", email="existing1@example.com", password="password123")
        existing.hash_password()
        db.session.add(existing)
        db.session.commit()

        response = self.client.post(
            "/users/register",
            data={
                "username": "existing1",
                "email": "existing1@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
        )
        self.assertEqual(response.status_code, 200)
        users_count = len(db.session.scalars(select(User)).all())
        self.assertEqual(users_count, 1)

    # 3. Тестування входу, захисту сторінок та виходу користувача
    def test_login_and_logout_flow(self):
        """Успішний вхід відкриває доступ до /account та /users/, оновлює меню, а logout завершує сеанс."""
        user = User(username="oscar", email="oscar@example.com", password="secretpassword")
        user.hash_password()
        db.session.add(user)
        db.session.commit()

        # Неавторизований доступ до захищених сторінок перенаправляє на /users/login
        unauth_account = self.client.get("/users/account")
        self.assertEqual(unauth_account.status_code, 302)
        self.assertIn("/users/login", unauth_account.headers["Location"])

        unauth_users = self.client.get("/users/")
        self.assertEqual(unauth_users.status_code, 302)
        self.assertIn("/users/login", unauth_users.headers["Location"])

        # Вхід на сайт
        login_response = self.client.post(
            "/users/login",
            data={
                "email": "oscar@example.com",
                "password": "secretpassword",
                "remember": True,
            },
            follow_redirects=True,
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b"You have been logged in!", login_response.data)
        self.assertIn(b"Welcome, oscar!", login_response.data)
        self.assertIn(b"oscar@example.com", login_response.data)
        # Меню для авторизованого користувача: є Профіль та Вихід, немає Login/Register
        self.assertIn("/users/account".encode("utf-8"), login_response.data)
        self.assertIn("/users/logout".encode("utf-8"), login_response.data)
        self.assertNotIn(b">Register<", login_response.data)

        # Авторизований користувач перенаправляється з /register на /account
        reg_redirect = self.client.get("/users/register")
        self.assertEqual(reg_redirect.status_code, 302)
        self.assertIn("/users/account", reg_redirect.headers["Location"])

        # Авторизований користувач має доступ до списку всіх користувачів
        users_response = self.client.get("/users/")
        self.assertEqual(users_response.status_code, 200)
        self.assertIn(b"Users List (1)", users_response.data)
        self.assertIn(b"oscar", users_response.data)
        self.assertIn(b"oscar@example.com", users_response.data)

        # Вихід із системи
        logout_response = self.client.get("/users/logout", follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn(b"You have successfully logged out.", logout_response.data)

        # Після виходу доступ до /users/account знову закритий
        after_logout = self.client.get("/users/account")
        self.assertEqual(after_logout.status_code, 302)
        self.assertIn("/users/login", after_logout.headers["Location"])

    def test_login_invalid_credentials(self):
        """Невірний пароль не авторизує користувача."""
        user = User(username="oscar", email="oscar@example.com", password="secretpassword")
        user.hash_password()
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/users/login",
            data={
                "email": "oscar@example.com",
                "password": "wrongpassword",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid email or password.", response.data)


if __name__ == "__main__":
    unittest.main()
