import unittest
from datetime import datetime, timezone
from app import create_app, db
from app.posts.models import Post


class PostCRUDTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування тестового клієнта та in-memory бази даних."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Очищення сесії та видалення таблиць після тесту."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_post(self):
        """US01: Створити новий пост (POST /post/create)."""
        post_data = {
            "title": "New Tech Article",
            "content": "This is detailed text about Python and SQLAlchemy.",
            "category": "tech",
            "enabled": True
        }
        response = self.client.post("/post/create", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        created_post = db.session.scalar(db.select(Post).where(Post.title == "New Tech Article"))
        self.assertIsNotNone(created_post)
        self.assertEqual(created_post.content, "This is detailed text about Python and SQLAlchemy.")
        self.assertEqual(created_post.category, "tech")
        self.assertTrue(created_post.is_active)
        self.assertEqual(created_post.author, "Anonymous")
        self.assertIn("Post added successfully".encode("utf-8"), response.data)

        # Перевірка автора при наявності користувача в сесії
        with self.client.session_transaction() as sess:
            sess["username"] = "admin"

        auth_post_data = {
            "title": "Admin Announcement",
            "content": "Official announcement content.",
            "category": "news",
            "enabled": True
        }
        self.client.post("/post/create", data=auth_post_data, follow_redirects=True)
        admin_post = db.session.scalar(db.select(Post).where(Post.title == "Admin Announcement"))
        self.assertIsNotNone(admin_post)
        self.assertEqual(admin_post.author, "admin")

    def test_list_posts(self):
        """US02: Перегляд списку видимих постів за спаданням дати (GET /post)."""
        p1 = Post(
            title="Older Post",
            content="Content of older post",
            category="news",
            is_active=True,
            posted=datetime(2026, 1, 10, 10, 0)
        )
        p2 = Post(
            title="Newer Post",
            content="Content of newer post",
            category="publication",
            is_active=True,
            posted=datetime(2026, 2, 20, 15, 30)
        )
        p_hidden = Post(
            title="Hidden Inactive Post",
            content="Should not be visible in list",
            category="other",
            is_active=False,
            posted=datetime(2026, 3, 1, 12, 0)
        )
        db.session.add_all([p1, p2, p_hidden])
        db.session.commit()

        response = self.client.get("/post")
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertIn("Older Post".encode("utf-8"), data)
        self.assertIn("Newer Post".encode("utf-8"), data)
        self.assertNotIn("Hidden Inactive Post".encode("utf-8"), data)

        # Перевірка сортування за спаданням дати
        pos_newer = data.find("Newer Post".encode("utf-8"))
        pos_older = data.find("Older Post".encode("utf-8"))
        self.assertTrue(pos_newer < pos_older)

    def test_view_post_detail(self):
        """US03: Перегляд окремого поста (GET /post/<id>)."""
        post = Post(
            title="Detailed Architecture Overview",
            content="Full deep dive into microservices and monoliths.",
            category="publication",
            author="Architect",
            is_active=True
        )
        db.session.add(post)
        db.session.commit()

        response = self.client.get(f"/post/{post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Detailed Architecture Overview".encode("utf-8"), response.data)
        self.assertIn("Full deep dive into microservices and monoliths.".encode("utf-8"), response.data)
        self.assertIn("Architect".encode("utf-8"), response.data)
        self.assertIn("publication".encode("utf-8"), response.data)

    def test_update_post(self):
        """US04: Редагування поста (POST /post/<id>/update)."""
        post = Post(
            title="Initial Title",
            content="Initial Content",
            category="tech",
            is_active=True
        )
        db.session.add(post)
        db.session.commit()

        update_data = {
            "title": "Modified Title",
            "content": "Modified Content with new findings",
            "category": "publication",
            "enabled": True
        }
        response = self.client.post(f"/post/{post.id}/update", data=update_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Post updated successfully".encode("utf-8"), response.data)

        db.session.refresh(post)
        self.assertEqual(post.title, "Modified Title")
        self.assertEqual(post.content, "Modified Content with new findings")
        self.assertEqual(post.category, "publication")

    def test_delete_post(self):
        """US05: Видалення поста (POST /post/<id>/delete)."""
        post = Post(
            title="Post To Be Deleted",
            content="Temporary content",
            category="other",
            is_active=True
        )
        db.session.add(post)
        db.session.commit()
        post_id = post.id

        # GET запит показує форму підтвердження
        get_response = self.client.get(f"/post/{post_id}/delete")
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Delete Confirmation".encode("utf-8"), get_response.data)

        # POST запит видаляє пост
        post_response = self.client.post(f"/post/{post_id}/delete", follow_redirects=True)
        self.assertEqual(post_response.status_code, 200)
        self.assertIn("Post deleted successfully".encode("utf-8"), post_response.data)

        deleted = db.session.get(Post, post_id)
        self.assertIsNone(deleted)

    def test_lab8_relationships(self):
        """Lab 8: One-to-Many (User-Post) and Many-to-Many (Post-Tag) relationships."""
        from app.users.models import User
        from app.posts.models import Tag

        # Create user
        u1 = User(username="author1", email="author1@ex.com", password="pwd")
        u2 = User(username="author2", email="author2@ex.com", password="pwd")
        t1 = Tag(name="Tech")
        t2 = Tag(name="Python")
        db.session.add_all([u1, u2, t1, t2])
        db.session.commit()

        # Create post via client with author_id and tags
        post_data = {
            "title": "Lab 8 Relationship Post",
            "content": "Testing relations with author and tags.",
            "category": "tech",
            "author_id": u1.id,
            "tags": [t1.id, t2.id],
            "enabled": True
        }
        res = self.client.post("/post/create", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify post, user, and tags
        created = db.session.scalar(db.select(Post).where(Post.title == "Lab 8 Relationship Post"))
        self.assertIsNotNone(created)
        self.assertEqual(created.user_id, u1.id)
        self.assertEqual(created.user.username, "author1")
        self.assertIn(created, u1.posts)
        self.assertEqual(len(created.tags), 2)
        self.assertIn(created, t1.posts)
        self.assertIn(created, t2.posts)

        # Verify detail page renders author and tags
        detail_res = self.client.get(f"/post/{created.id}")
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn("author1@ex.com".encode("utf-8"), detail_res.data)
        self.assertIn("Tech".encode("utf-8"), detail_res.data)
        self.assertIn("Python".encode("utf-8"), detail_res.data)

    def test_404_not_found(self):
        """US06: 404 помилка при запиті неіснуючого поста (GET /post/9999)."""
        response = self.client.get("/post/99999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("404".encode("utf-8"), response.data)
        self.assertIn("Oops! Page Not Found".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
