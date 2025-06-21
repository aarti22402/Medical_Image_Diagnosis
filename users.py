
from flask_login import UserMixin

users = {
    "aarti": {"password": "aarti123"},
    "Nila": {"password": "nila123"},
    "prachi": {"password": "prachi123"},
    "saksiPatil": {"password": "saksi123"},
    "xyz": {"password": "xyz123"},
    "admin": {"password": "admin123"},
    "doctor1": {"password": "docpass"},
    "radiologist": {"password": "xray123"}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username  # Required by Flask-Login

    def get_id(self):
        return self.id

def get_user(username):
    if username in users:
        return User(username)
    return None

def add_user(username, password):
    if username not in users:
        users[username] = {"password": password}
        return True
    return False 
