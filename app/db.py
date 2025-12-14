from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class User:
    email: str
    password_hash: str

_USERS: Dict[str, User] = {}

def create_user(email: str, password_hash: str) -> User:
    u = User(email=email.lower().strip(), password_hash=password_hash)
    _USERS[u.email] = u
    return u

def get_user(email: str) -> Optional[User]:
    return _USERS.get(email.lower().strip())
