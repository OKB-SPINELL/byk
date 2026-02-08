import typing as ty  # noqa: F401

from asgiref.sync import async_to_sync
from django.db import transaction

from book_mgr.models import Book
from byk.task_broker import broker


class BookManager:

    @classmethod
    @transaction.atomic
    def quick_create_book(cls, isbn_number: str = None,
                          title: str = None,
                          tracking_number: str = None,
                          overwrite_existing: bool = False) -> 'Book':
        if not (isbn_number or title):
            raise ValueError("Either ISBN or Title must be provided to create a book.")

        if isbn_number and overwrite_existing:
            Book.objects.filter(isbn_number=isbn_number).delete()

        book = Book.objects.create(isbn_number=isbn_number, title=title, tracking_number=tracking_number)

        async_to_sync(broker.publish)(dict(
            pk=book.pk,
        ), channel="book_mgr.fetch_books")

        return book
