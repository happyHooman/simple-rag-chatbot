#!/usr/bin/env python3
"""Script to generate JWT tokens for testing and administration."""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.helpers.auth import create_access_token


def main() -> None:
    """Generate a JWT token."""
    print("=== JWT Token Generator ===\n")
    
    # Get user input
    subject = input("Enter subject/user (default: 'admin'): ").strip() or "admin"
    hours = input(f"Enter expiration hours (default: 24): ").strip()
    
    try:
        hours_int = int(hours) if hours else 24
    except ValueError:
        print("Invalid hours, using default (24)")
        hours_int = 24
    
    # Generate token
    token_data = {
        "sub": subject,
        "type": "access_token"
    }
    
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=hours_int)
    )
    
    print(f"\n✅ JWT Token Generated:\n")
    print(f"Subject: {subject}")
    print(f"Expires in: {hours_int} hours")
    print(f"\nToken:\n{token}\n")
    print(f"Use as: Authorization: Bearer {token}\n")


if __name__ == "__main__":
    main()

