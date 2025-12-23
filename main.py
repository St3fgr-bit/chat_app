from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid, secrets

app = FastAPI()

# In-memory storage
users = []
messages = []
tokens = {}  # user_code: token

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------------------
# HOME PAGE
# ---------------------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------------------
# REGISTER
# ---------------------------
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if any(u["username"] == username for u in users):
        return {"message": "Username already taken"}
    user_code = str(uuid.uuid4())
    user = {"username": username, "password": password, "code": user_code}
    users.append(user)
    return {"message": "User registered", "user": {"username": username, "code": user_code}}

# ---------------------------
# LOGIN
# ---------------------------
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    for user in users:
        if user["username"] == username and user["password"] == password:
            token = secrets.token_hex(16)
            tokens[user["code"]] = token
            return {"message": "Login successful", "user": {"username": username, "code": user["code"], "token": token}}
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
def send_message(sender_code: str = Form(...), token: str = Form(...), receiver_username: str = Form(...), content: str = Form(...)):
    if tokens.get(sender_code) != token:
        return {"message": "Invalid token, access denied"}

    sender = next((u for u in users if u["code"] == sender_code), None)
    receiver = next((u for u in users if u["username"] == receiver_username), None)
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
    user_messages = [m for m in messages if m["to_code"] == user_code]
    return {"messages": user_messages}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)