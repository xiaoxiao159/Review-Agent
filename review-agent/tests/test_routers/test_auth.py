from datetime import datetime, timedelta

from jose import jwt


def test_expired_token_returns_401(client):
    token = jwt.encode(
        {
            "sub": "admin",
            "typ": "access",
            "jti": "x",
            "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
        },
        "change-me",
        algorithm="HS256",
    )
    response = client.get("/api/v1/reports/status/t1", headers={"authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_401"
