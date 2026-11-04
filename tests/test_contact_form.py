import unittest
from app import app


class ContactFormTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування тестового середовища."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_contact_page_get(self):
        """Тест відображення форми контактів GET /contact."""
        response = self.client.get("/contact")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Send a Message".encode("utf-8"), response.data)
        self.assertIn("name".encode("utf-8"), response.data)
        self.assertIn("email".encode("utf-8"), response.data)
        self.assertIn("phone".encode("utf-8"), response.data)
        self.assertIn("subject".encode("utf-8"), response.data)
        self.assertIn("message".encode("utf-8"), response.data)

    def test_contact_page_post_valid(self):
        """Тест відправлення валідних даних контактної форми."""
        valid_data = {
            "name": "Alex",
            "email": "alex@example.com",
            "phone": "+380501234567",
            "subject": "collaboration",
            "message": "Доброго дня! Пропоную співпрацю у спільному проєкті."
        }
        response = self.client.post("/contact", data=valid_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно надіслано".encode("utf-8"), response.data)

    def test_contact_page_post_invalid_name(self):
        """Тест валідації: занадто коротке ім'я (min=4)."""
        invalid_data = {
            "name": "Tom",  # 3 символи замість мінімум 4
            "email": "tom@example.com",
            "phone": "+380501234567",
            "subject": "feedback",
            "message": "Чудовий сайт!"
        }
        response = self.client.post("/contact", data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Помилка валідації форми".encode("utf-8"), response.data)

    def test_contact_page_post_invalid_phone(self):
        """Тест валідації: некоректний формат телефону (має бути +380XXXXXXXXX)."""
        invalid_data = {
            "name": "Mykola",
            "email": "mykola@example.com",
            "phone": "0501234567",  # без +380
            "subject": "question",
            "message": "Маю запитання щодо навчання."
        }
        response = self.client.post("/contact", data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Помилка валідації форми".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
