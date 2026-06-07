import sqlite3
import bcrypt
from datetime import datetime
import warnings
import asyncio
import atexit

# Suppress Windows asyncio socket cleanup warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message=".*_call_connection_lost.*")

if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False,
    timeout=5,
    isolation_level=None
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS uploads(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    file_name TEXT,
    upload_time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS validation_results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER,
    issue TEXT,
    ai_suggestion TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cleaned_files(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER,
    cleaned_file_name TEXT,
    cleaned_time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS uploaded_csv_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER,
    csv_content TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cleaned_csv_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER,
    csv_content TEXT
)
""")

conn.commit()


def create_user(email, password):

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        cursor.execute(
            """
            INSERT INTO users(email,password)
            VALUES (?,?)
            """,
            (
                email,
                hashed_password.decode()
            )
        )

        conn.commit()

        return True

    except:

        return False


def verify_user(email, password):

    cursor.execute(
        """
        SELECT password
        FROM users
        WHERE email=?
        """,
        (email,)
    )

    user = cursor.fetchone()

    if user:

        stored_password = user[0]

        if bcrypt.checkpw(
            password.encode(),
            stored_password.encode()
        ):
            return True

    return False


def save_upload(
    user_email,
    file_name
):

    cursor.execute(
        """
        INSERT INTO uploads(
            user_email,
            file_name,
            upload_time
        )
        VALUES (?,?,?)
        """,
        (
            user_email,
            file_name,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()

    return cursor.lastrowid


def save_validation(
    upload_id,
    issue,
    ai_suggestion
):

    cursor.execute(
        """
        INSERT INTO validation_results(
            upload_id,
            issue,
            ai_suggestion
        )
        VALUES (?,?,?)
        """,
        (
            upload_id,
            issue,
            ai_suggestion
        )
    )

    conn.commit()


def save_cleaned_file(
    upload_id,
    file_name
):

    cursor.execute(
        """
        INSERT INTO cleaned_files(
            upload_id,
            cleaned_file_name,
            cleaned_time
        )
        VALUES (?,?,?)
        """,
        (
            upload_id,
            file_name,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()


def save_uploaded_csv(
    upload_id,
    csv_content
):

    cursor.execute(
        """
        INSERT INTO uploaded_csv_data(
            upload_id,
            csv_content
        )
        VALUES (?,?)
        """,
        (
            upload_id,
            csv_content
        )
    )

    conn.commit()


def save_cleaned_csv(
    upload_id,
    csv_content
):

    cursor.execute(
        """
        INSERT INTO cleaned_csv_data(
            upload_id,
            csv_content
        )
        VALUES (?,?)
        """,
        (
            upload_id,
            csv_content
        )
    )

    conn.commit()


# 🔒 PRIVACY FIX: Filter history by user_email
def get_history(user_email):

    cursor.execute("""
    SELECT
        uploads.id,
        uploads.upload_time,
        uploads.file_name,
        uploaded_csv_data.csv_content,
        cleaned_csv_data.csv_content

    FROM uploads

    LEFT JOIN uploaded_csv_data
    ON uploads.id = uploaded_csv_data.upload_id

    LEFT JOIN cleaned_csv_data
    ON uploads.id = cleaned_csv_data.upload_id

    WHERE uploads.user_email = ?

    ORDER BY uploads.id DESC
    """, (user_email,))

    return cursor.fetchall()


def get_issues(upload_id):

    cursor.execute("""
    SELECT issue
    FROM validation_results
    WHERE upload_id=?
    """, (upload_id,))

    return cursor.fetchall()


# Cleanup handler
def _cleanup():
    try:
        conn.close()
    except:
        pass

atexit.register(_cleanup)