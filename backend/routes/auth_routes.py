from flask import Blueprint, jsonify, request

from services.auth_service import (
    change_password,
    get_profile,
    login_user,
    register_user,
    update_profile,
)

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    payload, status = register_user(
        email=(data.get("email") or "").strip().lower(),
        username=(data.get("username") or "").strip(),
        password=data.get("password") or "",
        role=(data.get("role") or "technician").strip().lower(),
    )
    return jsonify(payload), status


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    payload, status = login_user(
        email=(data.get("email") or "").strip().lower(),
        password=data.get("password") or "",
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", ""),
    )
    return jsonify(payload), status


@auth_bp.route("/auth/profile", methods=["GET"])
def profile_get():
    payload, status = get_profile(request.args.get("user_id", type=int))
    return jsonify(payload), status


@auth_bp.route("/auth/profile", methods=["PUT"])
def profile_put():
    data = request.get_json(silent=True) or {}
    payload, status = update_profile(
        user_id=data.get("user_id"),
        username=(data.get("username") or "").strip(),
    )
    return jsonify(payload), status


@auth_bp.route("/auth/change-password", methods=["POST"])
def password_change():
    data = request.get_json(silent=True) or {}
    payload, status = change_password(
        user_id=data.get("user_id"),
        current_password=data.get("current_password") or "",
        new_password=data.get("new_password") or "",
    )
    return jsonify(payload), status
