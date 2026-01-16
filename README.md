# Simple Chat Application – Backend

This project is a backend-only implementation of a simple chat application that allows two users to exchange messages and track read and unread message status.

The goal of this assignment is to demonstrate backend design, database modeling, API design, and correct handling of message read state. The focus is on correctness and clarity rather than UI or authentication.

---

## Technology Stack

- Python
- Flask
- SQLite

---

## Scope and Assumptions

- The application supports only two users, which are seeded in the database.
- Authentication and authorization are not implemented, as they are out of scope.
- The project focuses entirely on backend logic.
- A minimal or no UI approach is used, as allowed by the assignment.

---

## Database Design

The application uses **Option A: Read timestamp on messages** to track read and unread status.

### Tables

**users**
- `id` – unique identifier for the user
- `name` – user name

**conversations**
- `id` – unique conversation identifier
- `user1_id` – first participant
- `user2_id` – second participant

**messages**
- `id` – unique message identifier
- `conversation_id` – reference to the conversation
- `sender_id` – ID of the user who sent the message
- `content` – text message content
- `created_at` – timestamp when the message was sent
- `read_at` – timestamp when the message was read (NULL if unread)

---

## Read / Unread Message Logic

- A message is considered **unread** if `read_at` is NULL.
- A message is considered **read** if `read_at` contains a timestamp.
- Messages sent by the current user are always treated as read.
- When a user opens a conversation, all unread messages sent by the other user in that conversation are marked as read.
- Unread message count per conversation is calculated using:
  - `sender_id != current_user`
  - `read_at IS NULL`

This approach keeps the logic simple and efficient while meeting the assignment requirements.

---

## API Endpoints

### Send a Message
**POST** `/messages`

Request body:
```json
{
  "conversation_id": 1,
  "sender_id": 1,
  "content": "Hello"
}
