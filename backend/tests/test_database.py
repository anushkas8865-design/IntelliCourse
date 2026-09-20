from uuid import uuid4

from shared.database.database import SessionLocal
from shared.models.user import User


def test_database_connection_and_user_crud():
    db = SessionLocal()

    test_email = f"test_{uuid4()}@example.com"

    user = None

    try:
        # Create a temporary user
        user = User(
            name="Database Test User",
            email=test_email,
            password="temporary_password",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Verify the user was saved
        saved_user = db.query(User).filter(
            User.email == test_email
        ).first()

        assert saved_user is not None
        assert saved_user.name == "Database Test User"
        assert saved_user.email == test_email

        print("Database CRUD test successful.")

    finally:
        # Remove the temporary user if it was saved
        db.rollback()

        if user and user.user_id:
            saved_user = db.query(User).filter(
                User.user_id == user.user_id
            ).first()

            if saved_user:
                db.delete(saved_user)
                db.commit()

        db.close()