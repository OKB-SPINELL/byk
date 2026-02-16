# -*- coding: utf-8 -*-
import logging
import time
import typing as ty  # noqa: F401

import asgiref.sync
from authlib.jose import jwt
from byk.kv import redis
from django.conf import settings
from django.db import transaction

from accounts.constants import DEFAULT_TENANT
from accounts.models import User

LOG = logging.getLogger("byk")

TENANT_USERNAME_FAILURE_COUNT = (
    "tenant:{tenant_id}:username:{username}:password_auth_failure_count"
)
TENANT_USERNAME_FAILURE_LOCKED = (
    "tenant:{tenant_id}:username:{username}:password_auth_locked"
)


def lockdown_by_failure_count(count: int) -> int:
    if count < 5:
        return 0
    elif count < 10:
        return 2 ** (count - 5) * 60  # exponential backoff in seconds
    else:
        return 3600  # max lock of 1 hour


def username_is_email(username: str) -> bool:
    return "@" in username and "." in username


async def username_locked(username: str, tenant: str = DEFAULT_TENANT) -> bool:
    key = TENANT_USERNAME_FAILURE_LOCKED.format(tenant_id=tenant, username=username)
    locked = await redis.exists(key)
    return locked


async def lock_username(username: str, tenant: str = "default") -> None:
    failure_key = TENANT_USERNAME_FAILURE_COUNT.format(
        tenant_id=tenant, username=username
    )
    locked_key = TENANT_USERNAME_FAILURE_LOCKED.format(
        tenant_id=tenant, username=username
    )

    failure_count = await redis.incr(failure_key)
    lock_duration = lockdown_by_failure_count(failure_count)

    if lock_duration > 0:
        await redis.setex(locked_key, lock_duration, "1")

    return


async def unset_username_lock(username: str, tenant: str = DEFAULT_TENANT) -> None:
    failure_key = TENANT_USERNAME_FAILURE_COUNT.format(
        tenant_id=tenant, username=username
    )
    locked_key = TENANT_USERNAME_FAILURE_LOCKED.format(
        tenant_id=tenant, username=username
    )

    await redis.delete(failure_key)
    await redis.delete(locked_key)

    return


async def authenticate_user_by_password(
    username: str,
    password: str,
    tenant: str = DEFAULT_TENANT,
) -> ty.Optional[User]:
    if await username_locked(username, tenant):
        LOG.warning(
            "Authentication attempt for locked username '%s' in tenant '%s'",
            username,
            tenant,
        )
        return None

    query = User.objects.all()
    if DEFAULT_TENANT != tenant:
        query = query.filter(tenant__slug=tenant)

    try:
        if username_is_email(username):
            user = await query.aget(email=username)
        else:
            user = await query.aget(username=username)
    except User.DoesNotExist:
        await lock_username(username, tenant)
        LOG.warning(
            "Authentication failed for non-existing username '%s' in tenant '%s'",
            username,
            tenant,
        )
        return None

    if not user.check_password(password):
        await lock_username(username, tenant)
        LOG.warning(
            "Authentication failed for username '%s' in tenant '%s'", username, tenant
        )
        return None

    return user


def time_constant(target_duration_ms: int):
    def _decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()

            result = func(*args, **kwargs)

            elapsed = time.perf_counter() - start
            target = target_duration_ms / 1000.0
            if elapsed < target:
                time.sleep(target - elapsed)

            return result

        return wrapper

    return _decorator


class PasswordAuthenticator(object):
    @staticmethod
    def create_token(user: User) -> str:
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "tenant": user.tenant.slug if user.tenant else DEFAULT_TENANT,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600 * 24 * 7,  # 7 days expiry
        }

        token = jwt.encode(
            header=dict(typ="JWT", alg=settings.JWT_ALGORITHM),
            payload=payload,
            key=settings.JWT_SECRET_KEY,
        )
        return token.decode()

    @time_constant(400)
    async def authenticate(
        self, username: str, password: str, tenant: str = DEFAULT_TENANT
    ) -> ty.Tuple[ty.Optional[User], ty.Optional[str]]:
        user = await authenticate_user_by_password(username, password, tenant)
        if user:
            await unset_username_lock(username, tenant)
        else:
            return None, None

        token = self.create_token(user)

        return user, token
