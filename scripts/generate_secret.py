"""Generate a random SECRET_KEY for production deployment."""

import secrets

if __name__ == "__main__":
    print(secrets.token_hex(32))
