from app.core.config_db import SessionLocal
from app.models.user import User
from app.core import security


def create_users(start, end, role):
    session = SessionLocal()
    try:
        for i in range(start, end + 1):
            name = f"{role}{i}"
            email = f"{role}{i}@example.com"

            existing = session.query(User).filter(User.email == email).first()
            if existing:
                print(f"Skipped {email}, already exists")
                continue

            user_to_create = {
                "name": name,
                "department": "cse",
                "role": role,
                "email": email,
                "password": security.hash_password("Event@123"),
            }

            if role == "student":
                user_to_create["year"] = "4"

            user = User(**user_to_create)
            session.add(user)

        session.commit()
        print(f"✅ Users {role}{start} to {role}{end} created successfully.")
    except Exception as e:
        session.rollback()
        print("❌ Error:", e)
    finally:
        session.close()


if __name__ == "__main__":
    create_users(1, 10, "admin")
