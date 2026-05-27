from db import get_connection


def normalize_collection(collection: str | None) -> str:
    return collection or ""


def scoped_collection(user_id: int, collection: str | None) -> str:
    base = normalize_collection(collection)
    if not base:
        return ""
    return f"u{user_id}_{base}"


def display_collection(scoped_name: str, user_id: int) -> str:
    prefix = f"u{user_id}_"
    if scoped_name.startswith(prefix):
        return scoped_name[len(prefix) :]
    return scoped_name


def init_chat_messages_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            collection VARCHAR(100) NOT NULL DEFAULT '',
            user_id INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_collection (user_id, collection)
        )
        """
    )
    try:
        cursor.execute(
            "ALTER TABLE chat_messages ADD COLUMN user_id INT NOT NULL DEFAULT 0"
        )
        conn.commit()
    except Exception:
        conn.rollback()
    conn.commit()
    cursor.close()
    conn.close()


def save_chat_message(
    role: str, content: str, collection: str | None, user_id: int
):
    collection_key = normalize_collection(collection)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO chat_messages (role, content, collection, user_id)
        VALUES (%s, %s, %s, %s)
        """,
        (role, content, collection_key, user_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_chat_history(collection: str | None, user_id: int):
    collection_key = normalize_collection(collection)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE collection = %s AND user_id = %s
        ORDER BY id ASC
        """,
        (collection_key, user_id),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def delete_chat_history(collection: str | None, user_id: int):
    collection_key = normalize_collection(collection)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM chat_messages WHERE collection = %s AND user_id = %s",
        (collection_key, user_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
