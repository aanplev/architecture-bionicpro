from fastapi import FastAPI, Depends, HTTPException, Header
import clickhouse_connect
import jwt

app = FastAPI()

CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123

KEYCLOAK_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
REPLACE_WITH_REAL_PUBLIC_KEY
-----END PUBLIC KEY-----"""
KEYCLOAK_ALGORITHM = "RS256"
KEYCLOAK_AUDIENCE = "reports-backend"
KEYCLOAK_ISSUER = "http://keycloak:8080/realms/reports-realm"


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT
    )


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            KEYCLOAK_PUBLIC_KEY,
            algorithms=[KEYCLOAK_ALGORITHM],
            audience=KEYCLOAK_AUDIENCE,
            issuer=KEYCLOAK_ISSUER,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    return user_id


@app.get("/reports")
def get_report(
    user_id: str = Depends(get_current_user),
):
    client = get_clickhouse_client()

    result = client.query(
        """
        SELECT user_id, metric, report_date
        FROM report_mart
        WHERE user_id = %(user_id)s
        """,
        {"user_id": int(user_id)},
    )

    if not result.result_rows:
        return []

    return [
        {
            "user_id": row[0],
            "metric": row[1],
            "report_date": str(row[2]),
        }
        for row in result.result_rows
    ]
