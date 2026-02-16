# -*- coding: utf-8 -*-
import typing as ty  # noqa: F401

from byk.schemas import AUTHENTICATION_FAILURE, ErrorMessageSchema
from django.http import HttpResponse
from ninja.responses import codes_4xx
from ninja.throttling import AnonRateThrottle

from accounts.auth.passwords import PasswordAuthenticator
from accounts.schemas.accounts import TokenCreatedResponseSchema, UserLoginRequestSchema

from .router import router


@router.post(
    "/login",
    auth=None,
    throttle=[AnonRateThrottle("10/m")],
    response={200: TokenCreatedResponseSchema, codes_4xx: ErrorMessageSchema},
)
async def login(request, payload: UserLoginRequestSchema, response: HttpResponse):
    payload = payload.dict(exclude_unset=True)

    username = payload.get("username")
    password = payload.get("password")
    tenant = payload.get("tenant")

    p = PasswordAuthenticator()
    __, token = await p.authenticate(username, password, tenant)

    response.set_cookie(
        "access_token", token, httponly=True, secure=True, samesite="Lax"
    )

    if not token:
        return 401, {
            "error_code": AUTHENTICATION_FAILURE,
            "message": "User or password is invalid",
        }

    return 200, {"access_token": token}
