# -*- coding: utf-8 -*-
import base64
import typing as ty  # noqa: F401

import uuid


def generate_safe_id(prefix: str = None) -> str:
    key = uuid.uuid7()
    safe_id = base64.urlsafe_b64encode(key.bytes).rstrip(b'=').decode('ascii')
    if prefix:
        safe_id = f'{prefix}-{safe_id}'

    return safe_id
