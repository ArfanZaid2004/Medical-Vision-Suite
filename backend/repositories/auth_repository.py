from core.db import get_db_connection


def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, email, username, role, password_hash FROM users WHERE email = %s",
            (email,),
        )
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def email_exists(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        return bool(cur.fetchone())
    finally:
        cur.close()
        conn.close()


def create_user(email, username, password_hash, role):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            (email, username, password_hash, role),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def log_login_event(email, success, ip_address, user_agent):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO login_events (email, success, ip_address, user_agent)
            VALUES (%s, %s, %s, %s)
            """,
            (email, success, ip_address, user_agent[:255]),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_user_profile(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, email, username, role, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_user_for_update(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def update_username(user_id, username):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        conn.commit()
        cur.execute("SELECT id, email, username, role FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_user_password_hash(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def update_password_hash(user_id, password_hash):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_user_role(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return row["role"] if row else None
    finally:
        cur.close()
        conn.close()
