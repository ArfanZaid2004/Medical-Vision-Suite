from repositories.auth_repository import get_user_role
from repositories.history_repository import (
    get_history_rows_for_doctor,
    get_history_rows_for_user,
)
from core.utils import build_image_url


def get_history(user_id):
    if not user_id:
        return {"error": "user_id is required"}, 400

    role = get_user_role(user_id)
    if not role:
        return {"error": "User not found"}, 404

    rows = get_history_rows_for_doctor() if role == "doctor" else get_history_rows_for_user(user_id)
    for row in rows:
        row["image_url"] = build_image_url(row.get("image_filename"))
    return rows, 200
