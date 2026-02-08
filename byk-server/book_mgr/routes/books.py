# -*- coding: utf-8 -*-
import typing as ty  # noqa: F401

from django.db.models import Q
from django.db.utils import IntegrityError
from ninja.responses import codes_4xx
from byk.schemas import ErrorMessageSchema, ERROR_OBJECT_NOT_FOUND, ERROR_OBJECT_EXISTS, SUCCEED
from book_mgr.schemas import BookSchema, BookCreateSchema, BookQuickCreatePostIn
from book_mgr.models import Book
from .router import router
from book_mgr.providers.book_manager import BookManager


@router.get("/", response={
    200: ty.List[BookSchema],
})
def list_books(request):
    """
    Retrieve a list of all books in the system.
    """

    books = Book.objects.select_related('location').all()
    return list(books)


@router.get("/{book_id}/", response={
    200: BookSchema,
    codes_4xx: ErrorMessageSchema
})
def retrieve_book(request, book_id: int | str):
    """
    Retrieve details of a specific book by its ID.
    """
    try:
        book = Book.objects.select_related('location') \
            .filter(Q(id=book_id) | Q(isbn_number=book_id)) \
            .get()
        return book
    except Book.DoesNotExist:
        return 404, {"message": "Book not found", "error_code": ERROR_OBJECT_NOT_FOUND}


@router.post('/', response={
    201: BookSchema,
    codes_4xx: ErrorMessageSchema
})
def create_book(request, payload: BookCreateSchema):
    """
    Create a new book entry in the system.
    """
    book_data = payload.dict(exclude_unset=True)

    try:
        book = Book.objects.create(**book_data)
    except IntegrityError as e:
        return 400, {
            "message": "Book with given ISBN already exists",
            "error_code": ERROR_OBJECT_EXISTS
        }

    book.refresh_from_db()
    return 201, book


@router.post('/quick-create', response={
    201: BookSchema,
    codes_4xx: ErrorMessageSchema
})
def create_book_quick(request, payload: BookQuickCreatePostIn):
    """
    dGFcK67U
    Create a new book entry in the system.
    """

    book = BookManager.quick_create_book(isbn_number=payload.isbn_number,
                                         title=payload.title,
                                         tracking_number=payload.tracking_number,
                                         overwrite_existing=payload.overwrite_existing)

    book.refresh_from_db()
    return 201, book


@router.put('/{book_id}/', response={
    200: BookSchema,
    codes_4xx: ErrorMessageSchema
})
def update_book(request, book_id: int | str, payload: BookCreateSchema):
    """
    Update an existing book's details by its ID.
    """
    try:
        book = Book.objects.filter(Q(id=book_id) | Q(isbn_number=book_id)).get()
    except Book.DoesNotExist:
        return 404, {"message": "Book not found", "error_code": ERROR_OBJECT_NOT_FOUND}

    book_data = payload.dict(exclude_unset=True)

    for field, value in book_data.items():
        setattr(book, field, value)

    try:
        book.save()
    except IntegrityError as e:
        return 400, {
            "message": "Book with given ISBN already exists",
            "error_code": ERROR_OBJECT_EXISTS
        }

    book.refresh_from_db()
    return 200, book


@router.delete('/{book_id}/', response={
    204: None,
    codes_4xx: ErrorMessageSchema
})
def delete_book(request, book_id: int | str):
    """
    Delete a book from the system by its ID.
    """
    try:
        book = Book.objects.filter(Q(id=book_id) | Q(isbn_number=book_id)).get()
    except Book.DoesNotExist:
        return 404, {"message": "Book not found", "error_code": ERROR_OBJECT_NOT_FOUND}

    book.delete()
    return 204, None
