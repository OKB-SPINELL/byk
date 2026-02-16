# -*- coding: utf-8 -*-
import logging
import typing as ty  # noqa: F401

from authlib.jose import JoseError, jwt
from django.conf import settings
from ninja.security import HttpBearer

from byk.schemas import NOT_AUTHENTICATED

LOG = logging.getLogger("django")


class TokenAuth(HttpBearer):
    def authenticate(self, request, token: str) -> ty.Optional[ty.Dict[str, ty.Any]]:
        try:
            claims = jwt.decode(token, settings.JWT_SECRET_KEY)
            claims.validate()

            uid = claims.get(
                "sub"
            )  # may be an Auth0 user id - shall be injected to Django Admin's user model
            if not uid:
                return None

            return claims
        except JoseError as e:
            LOG.debug("JWT decode error: %s", e)


token_auth = TokenAuth()


def on_invalid_token(apis):
    def _wrap(request, exc):
        return apis.create_response(
            request, {"message": str(exc), "error_code": NOT_AUTHENTICATED}, status=401
        )

    return _wrap
