import mysql.connector

from core.config import DB_CONFIG


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            username VARCHAR(100) NOT NULL DEFAULT '',
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("SHOW COLUMNS FROM users LIKE 'username'")
    if cur.fetchone() is None:
        cur.execute(
            "ALTER TABLE users ADD COLUMN username VARCHAR(100) NOT NULL DEFAULT '' AFTER email"
        )
    cur.execute("SHOW COLUMNS FROM users LIKE 'role'")
    if cur.fetchone() is None:
        cur.execute(
            "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'technician'"
        )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS login_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            success BOOLEAN NOT NULL,
            ip_address VARCHAR(64),
            user_agent VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            entered_by_role VARCHAR(20) NOT NULL DEFAULT 'technician',
            scan_type VARCHAR(50) NOT NULL,
            prediction VARCHAR(100) NOT NULL,
            confidence DECIMAL(5,2) NOT NULL,
            patient_name VARCHAR(255) NOT NULL,
            patient_age INT NOT NULL,
            patient_sex VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    cur.execute("SHOW COLUMNS FROM predictions LIKE 'entered_by_role'")
    if cur.fetchone() is None:
        cur.execute(
            "ALTER TABLE predictions ADD COLUMN entered_by_role VARCHAR(20) NOT NULL DEFAULT 'technician' AFTER user_id"
        )
    cur.execute("SHOW COLUMNS FROM predictions LIKE 'image_filename'")
    if cur.fetchone() is None:
        cur.execute(
            "ALTER TABLE predictions ADD COLUMN image_filename VARCHAR(255) NULL AFTER patient_sex"
        )
    cur.execute(
        """
        UPDATE users
        SET username = SUBSTRING_INDEX(email, '@', 1)
        WHERE username IS NULL OR TRIM(username) = ''
        """
    )
    conn.commit()
    cur.close()
    conn.close()
