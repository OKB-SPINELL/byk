import typing as ty  # noqa: F401
import uuid

from asgiref.sync import async_to_sync
from byk.task_broker import broker
from django.db import transaction

from book_mgr.models import Book


class BookManager:
    @classmethod
    @transaction.atomic
    def quick_create_book(
        cls,
        book_id: ty.Optional[uuid.UUID] = None,
        isbn_number: str = None,
        title: str = None,
        tracking_number: str = None,
        overwrite_existing: bool = False,
    ) -> "Book":
        if not book_id:
            book_id = uuid.uuid7()

        if isbn_number and overwrite_existing:
            Book.objects.filter(isbn_number=isbn_number).delete()

        book = Book.objects.create(
            id=book_id,
            isbn_number=isbn_number,
            title=title,
            tracking_number=tracking_number,
        )

        async_to_sync(broker.publish)(
            dict(
                pk=book.pk,
            ),
            channel="book_mgr.fetch_books",
        )

        return book
