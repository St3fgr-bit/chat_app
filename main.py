from fastapi import FastAPI
from datetime import datetime
import uuid

import secrets

tokens = {}  # user_code: token

# Update login endpoint
@app.post("/login")
def login(username: str, password: str):
    for user in users:
        if user["username"] == username and user["password"] == password:
            token = secrets.token_hex(16)
            tokens[user["code"]] = token
            return {"message": "Login successful", "user": {"username": username, "code": user["code"], "token": token}}
    return {"message": "Invalid username or password"}

app = FastAPI()

# In-memory storage
users = []
messages = []

# ---------------------------
# REGISTER
# ---------------------------
@app.post("/register")
def register(username: str, password: str):
    # Check if username already exists
    if any(u["username"] == username for u in users):
        return {"message": "Username already taken"}

    user_code = str(uuid.uuid4())
    user = {
        "username": username,
        "password": password,  # plain text for now (learning purposes)
        "code": user_code
    }
    users.append(user)
    return {"message": "User registered", "user": {"username": username, "code": user_code}}

# ---------------------------
# LOGIN
# ---------------------------
@app.post("/login")
def login(username: str, password: str):
    for user in users:
        if user["username"] == username and user["password"] == password:
            return {"message": "Login successful", "user": {"username": username, "code": user["code"]}}
    return {"message": "Invalid username or password"}

# ---------------------------
# LIST USERS
# ---------------------------
@app.get("/users")
def list_users():
    return {"users": [{"username": u["username"], "code": u["code"]} for u in users]}

# ---------------------------
# SEND MESSAGE
# ---------------------------
@app.post("/send_message")
def send_message(sender_code: str, token: str, receiver_username: str, content: str):
    if tokens.get(sender_code) != token:
        return {"message": "Invalid token, access denied"}
    # rest of yoour send message logic
    
    if not sender or not receiver:
        return {"message": "Sender or receiver not found"}

    message = {
        "from_code": sender_code,
        "from_username": sender["username"],
        "to_code": receiver["code"],
        "to_username": receiver["username"],
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    return {"message": "Message sent", "message_data": message}

# ---------------------------
# VIEW INBOX
# ---------------------------
@app.get("/inbox/{user_code}")
def inbox(user_code: str, token: str):
    if tokens.get(user_code) != token:
        return {"message": "Invalid token, access denied"}
    # rest of your inbox logic
