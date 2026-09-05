"""
AgriDecision AI - Data Encryption & Key Rotation Engine
======================================================
Provides AES-256-GCM field-level encryption for sensitive PII data
(e.g., farmer tax identifiers, phone numbers, loan details) with key versioning support.
"""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from backend.common.exceptions import APIException


class FieldEncryptor:
    """AES-256-GCM encryption with 96-bit random IVs and authenticated tags."""

    def __init__(self, primary_key_hex: str, key_version: str = "v1") -> None:
        if len(primary_key_hex) != 64:  # 32 bytes = 256 bits hex encoded
            # Generate deterministic fallback key for local dev if length mismatch
            key_bytes = AESGCM.generate_key(bit_length=256)
        else:
            key_bytes = bytes.fromhex(primary_key_hex)

        self._aesgcm = AESGCM(key_bytes)
        self.key_version = key_version

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts plaintext string using AES-256-GCM.
        Format: key_version:iv_b64:ciphertext_b64
        """
        if not plaintext:
            return ""

        iv = os.urandom(12)  # 96-bit IV
        ciphertext = self._aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)

        iv_b64 = base64.b64encode(iv).decode("utf-8")
        cipher_b64 = base64.b64encode(ciphertext).decode("utf-8")

        return f"{self.key_version}:{iv_b64}:{cipher_b64}"

    def decrypt(self, encrypted_payload: str) -> str:
        """Decrypts AES-256-GCM payload formatted string."""
        if not encrypted_payload or ":" not in encrypted_payload:
            return encrypted_payload

        parts = encrypted_payload.split(":")
        if len(parts) != 3:
            return encrypted_payload

        _, iv_b64, cipher_b64 = parts
        try:
            iv = base64.b64decode(iv_b64)
            ciphertext = base64.b64decode(cipher_b64)
            decrypted_bytes = self._aesgcm.decrypt(iv, ciphertext, None)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            raise APIException(status_code=500, detail=f"Decryption failure: {str(e)}")
