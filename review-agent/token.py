from datetime import datetime, timedelta
from jose import jwt

JWT_SECRET = "xiaoxiao"
JWT_ALGORITHM = "HS256"

def create_access_token():
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode = {"sub": "test-user", "exp": expire}
    print(jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM))

if __name__ == "__main__":
    create_access_token()
