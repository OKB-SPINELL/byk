# -*- coding: utf-8 -*-
import typing as ty  # noqa: F401
import uuid

from django.db import models

FAKE_ISBN_PREFIX = '000'


class BookStorage(models.Model):
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Storage at {self.location} with capacity {self.capacity}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)
    biography = models.TextField(blank=True, null=True)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.name



class Book(models.Model):
    # UUID7 for time-sortable IDs
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid7)
    title = models.CharField(max_length=200, blank=True, null=True)
    authors = models.JSONField(default=list, blank=True)
    published_date = models.CharField(max_length=32, blank=True, null=True)

    isbn_number = models.CharField(max_length=13, unique=True, blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True, default=None)
    cover_image = models.URLField(blank=True, null=True)
    language = models.CharField(max_length=30, null=True, blank=True)

    location = models.ForeignKey(BookStorage, on_delete=models.CASCADE, related_name='books',
                                 blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    comments = models.TextField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True, default=None)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def is_fake_isbn(self) -> bool:
        if not self.isbn_number:
            return True

        if self.isbn_number.startswith(FAKE_ISBN_PREFIX):
            return True

        return False

    def __str__(self) -> str:
        return f"{self.title} by {', '.join(self.authors or list())}"
