from app.infrastructure.security.jwt import create_access_token, decode_access_token
from app.infrastructure.security.password import hash_password, verify_password
from app.infrastructure.security.tokens import create_opaque_token, hash_token


def test_password_hash_and_verify():
    hashed = hash_password("Password123")

    assert hashed != "Password123"
    assert verify_password("Password123", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_roundtrip():
    token = create_access_token("user-id", {"role": "student"})
    payload = decode_access_token(token)

    assert payload["sub"] == "user-id"
    assert payload["role"] == "student"
    assert payload["type"] == "access"


def test_refresh_token_hash_is_stable_and_not_plaintext():
    token = create_opaque_token()

    assert len(token) >= 32
    assert hash_token(token) == hash_token(token)
    assert hash_token(token) != token

