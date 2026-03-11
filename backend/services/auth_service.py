from werkzeug.security import check_password_hash, generate_password_hash

from repositories import auth_repository


def register_user(email, username, password, role):
    if role not in {"doctor", "technician"}:
        return {"error": "Invalid role"}, 400
    if not email or not username or not password:
        return {"error": "Username, email and password are required"}, 400
    if len(password) < 6:
        return {"error": "Password must be at least 6 characters"}, 400
    if len(username) < 3:
        return {"error": "Username must be at least 3 characters"}, 400
    if auth_repository.email_exists(email):
        return {"error": "Email already registered"}, 409

    auth_repository.create_user(email, username, generate_password_hash(password), role)
    return {"message": "User registered"}, 201


def login_user(email, password, ip_address, user_agent):
    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = auth_repository.get_user_by_email(email)
    success = bool(user and check_password_hash(user["password_hash"], password))
    auth_repository.log_login_event(email, success, ip_address, user_agent or "")

    if not success:
        return {"error": "Invalid email or password"}, 401

    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
        },
    }, 200


def get_profile(user_id):
    if not user_id:
        return {"error": "user_id is required"}, 400
    user = auth_repository.get_user_profile(user_id)
    if not user:
        return {"error": "User not found"}, 404
    return user, 200


def update_profile(user_id, username):
    if not user_id:
        return {"error": "user_id is required"}, 400
    if len(username) < 3:
        return {"error": "Username must be at least 3 characters"}, 400
    existing = auth_repository.get_user_for_update(user_id)
    if not existing:
        return {"error": "User not found"}, 404
    updated = auth_repository.update_username(user_id, username)
    return {"message": "Profile updated", "user": updated}, 200


def change_password(user_id, current_password, new_password):
    if not user_id:
        return {"error": "user_id is required"}, 400
    if not current_password or not new_password:
        return {"error": "Current and new password are required"}, 400
    if len(new_password) < 6:
        return {"error": "New password must be at least 6 characters"}, 400

    user = auth_repository.get_user_password_hash(user_id)
    if not user:
        return {"error": "User not found"}, 404
    if not check_password_hash(user["password_hash"], current_password):
        return {"error": "Current password is incorrect"}, 401

    auth_repository.update_password_hash(user_id, generate_password_hash(new_password))
    return {"message": "Password changed successfully"}, 200
