"""Admin authentication primitives. No default credentials or secrets."""
import os
import time
import hmac
import hashlib
import secrets
import base64
import json

TTL = 8 * 3600

def _secret():
    value = os.environ.get("AUTO_PARTS_SESSION_SECRET", "")
    if len(value) < 32:
        raise RuntimeError("Session secret is not configured")
    return value.encode()

def verify_password(password):
    # Format: salt_hex:iterations:digest_hex; PBKDF2-HMAC-SHA256.
    try:
        salt, rounds, expected = os.environ["AUTO_PARTS_PASSWORD_HASH"].split(":")
        rounds = int(rounds)
        if not 600000 <= rounds <= 2000000 or len(password) > 1024:
            return False
        salt = bytes.fromhex(salt)
        expected = bytes.fromhex(expected)
        if len(salt) < 16 or len(expected) != 32:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
        return hmac.compare_digest(actual, expected)
    except (KeyError, ValueError, TypeError, AttributeError):
        return False

def issue_session():
    payload = json.dumps({"exp": int(time.time()) + TTL, "nonce": secrets.token_hex(16)}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode()
    signature = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    return body + "." + signature

def valid_session(token):
    try:
        if not token or len(token) > 1024:
            return False
        body, signature = token.split(".")
        expected = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return False
        payload = json.loads(base64.urlsafe_b64decode(body))
        return int(time.time()) < payload["exp"] <= int(time.time()) + TTL
    except (ValueError, TypeError, KeyError, RuntimeError, AttributeError):
        return False

def session_cookie(token):
    return "auto_parts_session=" + token + "; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=" + str(TTL)

def clear_cookie():
    return "auto_parts_session=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0"
