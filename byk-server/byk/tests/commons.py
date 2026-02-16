# -*- coding: utf-8 -*-
from accounts.auth.passwords import PasswordAuthenticator
from accounts.models import User
from django.test import TestCase


class AuthenticatedTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="admin", password="admin")

        self.user = User.objects.create(username="admin", email="admin@okb-spinell.com")
        self.token = PasswordAuthenticator.create_token(self.user)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {self.token}"
