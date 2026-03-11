from core.db import get_db_connection


def get_history_rows_for_doctor():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                p.id, p.entered_by_role, p.scan_type, p.prediction, p.confidence,
                p.patient_name, p.patient_age, p.patient_sex, p.image_filename,
                p.created_at, u.email AS uploaded_by
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            """
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def get_history_rows_for_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                p.id, p.entered_by_role, p.scan_type, p.prediction, p.confidence,
                p.patient_name, p.patient_age, p.patient_sex, p.image_filename,
                p.created_at, u.email AS uploaded_by
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
            """,
            (user_id,),
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
