from core.db import get_db_connection


def insert_prediction(
    user_id,
    entered_by_role,
    scan_type,
    prediction,
    confidence,
    patient_name,
    patient_age,
    patient_sex,
    image_filename,
):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO predictions (
                user_id, entered_by_role, scan_type, prediction, confidence,
                patient_name, patient_age, patient_sex, image_filename
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                entered_by_role,
                scan_type,
                prediction,
                confidence,
                patient_name,
                patient_age,
                patient_sex,
                image_filename,
            ),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
