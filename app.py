from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "chat.db"


# --------------------
# Database setup
# --------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER,
            user2_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            sender_id INTEGER,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read_at DATETIME NULL
        )
    """)

    # Seed users
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'User A')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (2, 'User B')")

    # Seed conversation
    cursor.execute("""
        INSERT OR IGNORE INTO conversations (id, user1_id, user2_id)
        VALUES (1, 1, 2)
    """)

    conn.commit()
    conn.close()


# --------------------
# API: Send Message
# --------------------
@app.route("/messages", methods=["POST"])
def send_message():
    data = request.get_json()

    conversation_id = data.get("conversation_id")
    sender_id = data.get("sender_id")
    content = data.get("content")

    if not conversation_id or not sender_id or not content:
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (conversation_id, sender_id, content)
        VALUES (?, ?, ?)
    """, (conversation_id, sender_id, content))

    conn.commit()
    conn.close()

    return jsonify({"message": "Message sent successfully"}), 201


# --------------------
# API: Get conversations with unread count
# --------------------
@app.route("/conversations", methods=["GET"])
def get_conversations():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id AS conversation_id,
            COUNT(m.id) AS unread_count
        FROM conversations c
        LEFT JOIN messages m
            ON c.id = m.conversation_id
            AND m.sender_id != ?
            AND m.read_at IS NULL
        WHERE c.user1_id = ? OR c.user2_id = ?
        GROUP BY c.id
    """, (user_id, user_id, user_id))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "conversation_id": row[0],
            "unread_count": row[1]
        })

    return jsonify(result), 200


# --------------------
# API: Get messages of a conversation
# --------------------
@app.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
def get_messages(conversation_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            sender_id,
            content,
            created_at,
            read_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
    """, (conversation_id,))

    rows = cursor.fetchall()
    conn.close()

    messages = []
    for row in rows:
        messages.append({
            "id": row[0],
            "sender_id": row[1],
            "content": row[2],
            "created_at": row[3],
            "read_at": row[4]
        })

    return jsonify(messages), 200


# --------------------
# API: Mark messages as read (STEP 4D)
# --------------------
@app.route("/conversations/<int:conversation_id>/read", methods=["POST"])
def mark_as_read(conversation_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE messages
        SET read_at = CURRENT_TIMESTAMP
        WHERE conversation_id = ?
        AND sender_id != ?
        AND read_at IS NULL
    """, (conversation_id, user_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Messages marked as read"}), 200


# --------------------
# Home route
# --------------------
@app.route("/")
def home():
    return "Chat backend is running"


# --------------------
# App start
# --------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
