import os

from flask import request

from core.config import ALLOWED_EXTENSIONS


def is_allowed_image(filename):
    _, ext = os.path.splitext(filename or "")
    return ext.lower() in ALLOWED_EXTENSIONS


def build_image_url(filename):
    if not filename:
        return None
    return f"{request.host_url.rstrip('/')}/uploads/{filename}"
