from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import clickhouse_connect
import jwt
import requests
import logging
from functools import lru_cache
from jwt.algorithms import RSAAlgorithm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123

JWKS_URL = "http://keycloak:8080/realms/reports-realm/protocol/openid-connect/certs"


@lru_cache
def get_jwks():
    logger.info("Fetching JWKS from Keycloak")
    r = requests.get(JWKS_URL, timeout=5)
    r.raise_for_status()
    return r.json()


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
    )


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = get_jwks()

        jwk = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])
        public_key = RSAAlgorithm.from_jwk(jwk)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
            },
        )

        logger.info("JWT valid for user %s", payload["sub"])
        return payload["sub"]

    except Exception:
        logger.exception("JWT validation failed")
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reports")
def reports(user_id: str = Depends(get_current_user)):
    logger.info("REPORT REQUEST for user_id=%s", user_id)

    client = get_clickhouse_client()

    result = client.query(
        """
        SELECT user_id, metric, report_date
        FROM report_mart
        WHERE user_id = %(user_id)s
        """,
        {"user_id": user_id},
    )

    logger.info("ROWS FOUND: %d", len(result.result_rows))

    return [
        {
            "user_id": r[0],
            "metric": r[1],
            "report_date": str(r[2]),
        }
        for r in result.result_rows
    ]
