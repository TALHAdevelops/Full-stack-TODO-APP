import os
import sys
from getpass import getpass
from better_auth.utils import hashPassword

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db import get_session, engine
from backend.models import User
from sqlmodel import Session

def main():
    """Script to create a new user for testing."""
    print("--- Create a new TaskFlow test user ---")
    
    email = input("Enter email: ")
    if not email:
        print("Email cannot be empty.")
        return

    password = getpass("Enter password (min 8 chars): ")
    if len(password) < 8:
        print("Password is too short.")
        return

    name = input("Enter name (optional): ")

    hashed_password = hashPassword(password)
    
    print("\nCreating user...")

    try:
        with Session(engine) as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"Error: User with email '{email}' already exists.")
                return

            new_user = User(
                id=f"user-{os.urandom(4).hex()}",
                email=email,
                name=name if name else None,
                password_hash=hashed_password
            )
            
            session.add(new_user)
            session.commit()
            
            print(f"\n✅ User '{email}' created successfully!")
            print(f"   User ID: {new_user.id}")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
