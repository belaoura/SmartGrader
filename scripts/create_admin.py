"""CLI script to create the initial admin account.

Usage:
    python -m scripts.create_admin --email admin@school.dz --password yourpassword
"""

import argparse
import sys

from app import create_app
from app.models.user import User
from app.services.auth_service import create_teacher


def main():
    parser = argparse.ArgumentParser(description="Create the initial admin account")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password (min 8 chars)")
    parser.add_argument("--name", default="Admin", help="Admin display name")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(is_admin=True).first()
        if existing:
            print(f"Error: Admin already exists ({existing.email}). Aborting.")
            sys.exit(1)

        user = create_teacher(
            email=args.email,
            password=args.password,
            name=args.name,
            is_admin=True,
        )
        print(f"Admin account created: {user.email} (id={user.id})")


if __name__ == "__main__":
    main()
