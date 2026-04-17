import secrets


def generate_otp_code() -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(6))