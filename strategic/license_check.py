import os
import json
import base64
import subprocess
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

PUBLIC_KEY_B64 = "p/ufAhon+HsTqL1I914cpoYv1tr2akdkHGrFIAeVanI="


def get_machine_id():
    result = subprocess.run(
        ["wmic", "csproduct", "get", "UUID"],
        capture_output=True, text=True
    )
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    return lines[1] if len(lines) > 1 else None


def check_license(filename="license.dat"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, filename)

    if not os.path.exists(path):
        raise RuntimeError("فایل لایسنس (license.dat) پیدا نشد.")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    payload = data["payload"].encode()
    signature = base64.b64decode(data["signature"])

    public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBLIC_KEY_B64))
    try:
        public_key.verify(signature, payload)
    except InvalidSignature:
        raise RuntimeError("فایل لایسنس نامعتبر است (امضا تطابق ندارد).")

    payload_data = json.loads(payload)
    current_machine = get_machine_id()
    if payload_data.get("machine_id") != current_machine:
        raise RuntimeError("این لایسنس برای این سیستم صادر نشده است.")

    return True
