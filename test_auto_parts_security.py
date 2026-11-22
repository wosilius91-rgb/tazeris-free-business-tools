"""Security regression checks for administrator sessions and uploaded image bytes."""
import os
import unittest
from unittest.mock import patch

import auto_parts_auth as auth
import auto_parts_storage as storage


class AuthenticationSecurityTests(unittest.TestCase):
    def test_session_signature_expiry_and_cookie_flags(self):
        with patch.dict(os.environ, {"AUTO_PARTS_SESSION_SECRET": "s" * 48}):
            token = auth.issue_session()
            self.assertTrue(auth.valid_session(token))
            body, signature = token.split(".")
            self.assertFalse(auth.valid_session(body + "." + ("0" if signature[0] != "0" else "1") + signature[1:]))
            self.assertFalse(auth.valid_session(token + "garbage"))
            cookie = auth.session_cookie(token)
            for flag in ("Secure", "HttpOnly", "SameSite=Strict"):
                self.assertIn(flag, cookie)
            with patch.object(auth.time, "time", return_value=auth.time.time() + auth.TTL + 1):
                self.assertFalse(auth.valid_session(token))

    def test_missing_secret_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(auth.valid_session("invalid.token"))
            with self.assertRaises(RuntimeError):
                auth.issue_session()

    def test_missing_password_hash_denies_login(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(auth.verify_password("password"))


class ImageSecurityTests(unittest.TestCase):
    def test_invalid_images_rejected_before_database(self):
        for raw, mime in [
            (b"", "image/png"),
            (b"<script>alert(1)</script>", "image/png"),
            (b"RIFF1234NOTWEBP", "image/webp"),
            (b"\xff\xd8\xff", "text/html"),
            (b"x" * (storage.MAX_IMAGE + 1), "image/jpeg"),
        ]:
            with self.subTest(mime=mime, size=len(raw)):
                with self.assertRaises(ValueError):
                    storage.put_image(raw, mime)


if __name__ == "__main__":
    unittest.main()
