import sys
sys.path.insert(0, '.')

from database import get_db, User
from schemas import UserCreate
from auth import get_password_hash

# Test if we can create a user
db = next(get_db())

test_user = UserCreate(
    name="Test User",
    email="testuser@example.com",
    role="reviewer",
    password="test123"
)

print(f"Creating user: {test_user.name} ({test_user.email})")
print(f"Role: {test_user.role}")

# Check if user exists
existing = db.query(User).filter(User.email == test_user.email).first()
if existing:
    print(f"User already exists with ID: {existing.id}")
else:
    print("User doesn't exist, would create new user")
    hashed_password = get_password_hash(test_user.password)
    print(f"Password hashed successfully: {hashed_password[:20]}...")

print("\nTest completed!")
