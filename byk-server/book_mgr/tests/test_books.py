import uuid
from unittest.mock import AsyncMock, patch

from byk.tests.commons import AuthenticatedTestCase

from book_mgr.models import Book


class TestBooks(AuthenticatedTestCase):
    @patch("book_mgr.providers.book_manager.broker.publish", new_callable=AsyncMock)
    def test_quick_create_book(self, mock_publish):
        url = "/api/v1/books/quick-create"

        payload = {
            "book_id": str(uuid.uuid7()),
            "isbn_number": "978-3-16-148410-0",
        }

        res = self.client.post(url, data=payload, content_type="application/json")

        book = Book.objects.first()

        self.assertIsNotNone(book.id)
        self.assertEqual(book.isbn_number, "978-3-16-148410-0".replace("-", ""))

        self.assertTrue(mock_publish.publish.called)
