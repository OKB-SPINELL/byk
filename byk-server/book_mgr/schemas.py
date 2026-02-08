# -*- coding: utf-8 -*-
import typing as ty  # noqa: F401

from pydantic import Field, field_validator
from ninja import ModelSchema, Schema
from .models import Book, BookStorage, Tag


class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        exclude = ["comments"]


class BookStorageSchema(ModelSchema):

    class Meta:
        model = BookStorage
        exclude = ["comments"]


class BookSchema(ModelSchema):
    categories: ty.List[TagSchema] = Field(default_factory=list)
    location: BookStorageSchema = None

    @staticmethod
    def resolve_categories(book: Book) -> ty.List[Tag]:
        return list(book.tags.all())

    class Meta:
        model = Book
        fields = "__all__"


class BookCreateSchema(ModelSchema):

    class Meta:
        model = Book
        exclude = ["id", "location"]


class BookQuickCreatePostIn(Schema):
    isbn_number: ty.Optional[str] = None
    title: ty.Optional[str] = None
    tracking_number: ty.Optional[str] = None
    overwrite_existing: bool = False

    @field_validator('isbn_number', mode='before')
    @staticmethod
    def ensure_isbn_number(isbn_number: ty.Optional[str]) -> str | None:
        """ Add custom validation logic for ISBN-13 number if needed """
        if not isbn_number:
            return None

        # Normalize: remove hyphens and spaces
        s = isbn_number.replace('-', '').replace(' ', '')
        if not s.isdigit() or len(s) != 13:
            raise ValueError("ISBN-13 must contain 13 digits (hyphens/spaces allowed)")

        # Compute ISBN-13 checksum for the first 12 digits
        total = 0
        for i, ch in enumerate(s[:12]):
            digit = int(ch)
            total += digit if i % 2 == 0 else digit * 3
        check = (10 - (total % 10)) % 10

        if check != int(s[12]):
            raise ValueError("Invalid ISBN-13 checksum")

        return s
