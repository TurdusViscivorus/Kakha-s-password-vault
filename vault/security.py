from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from typing import Tuple

from cryptography.fernet import Fernet


@dataclass
class MasterSecret:
    salt: bytes
    password_hash: bytes


PBKDF2_ITERATIONS = 390000


def generate_salt(length: int = 16) -> bytes:
    return os.urandom(length)


def _pbkdf2(password: str, salt: bytes) -> bytes:
    return pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32)


def hash_password(password: str, salt: bytes) -> bytes:
    return _pbkdf2(password, salt)


def verify_password(password: str, salt: bytes, expected_hash: bytes) -> bool:
    return _pbkdf2(password, salt) == expected_hash


def derive_encryption_key(password: str, salt: bytes) -> bytes:
    raw_key = _pbkdf2(password, salt)
    return base64.urlsafe_b64encode(raw_key)


def build_fernet(password: str, salt: bytes) -> Fernet:
    key = derive_encryption_key(password, salt)
    return Fernet(key)


def encrypt(fernet: Fernet, plaintext: str) -> bytes:
    return fernet.encrypt(plaintext.encode("utf-8"))


def decrypt(fernet: Fernet, ciphertext: bytes) -> str:
    return fernet.decrypt(ciphertext).decode("utf-8")
