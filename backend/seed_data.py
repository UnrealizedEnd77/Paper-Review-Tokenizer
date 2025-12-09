"""
Seed script to populate the database with sample data for testing
Run this after starting the backend for the first time
"""
import requests
import time

BASE_URL = "http://localhost:8000"

# Sample users
users = [
    {
        "name": "Dr. Alice Johnson",
        "email": "alice@research.edu",
        "password": "password123",
        "role": "author",
        "affiliation": "Stanford University"
    },
    {
        "name": "Prof. Bob Smith",
        "email": "bob@review.edu",
        "password": "password123",
        "role": "reviewer",
        "affiliation": "MIT",
        "bio": "Machine Learning expert with 15 years experience",
        "expertise": "Machine Learning, AI, Deep Learning",
        "interests": "Computer Vision, NLP, Robotics"
    },
    {
        "name": "Dr. Carol Williams",
        "email": "carol@review.edu",
        "password": "password123",
        "role": "reviewer",
        "affiliation": "Harvard University",
        "bio": "Bioinformatics researcher",
        "expertise": "Bioinformatics, Genomics, Data Science",
        "interests": "Healthcare, Genetics, Statistical Analysis"
    },
    {
        "name": "Admin User",
        "email": "admin@system.com",
        "password": "admin123",
        "role": "admin",
        "affiliation": "System"
    }
]

def register_user(user_data):
    """Register a user"""
    print(f"Registering {user_data['name']}...")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_data
    )
    
    if response.status_code == 200:
        print(f"✅ {user_data['name']} registered successfully")
        user = response.json()
        
        # Update profile if reviewer
        if user_data['role'] == 'reviewer' and 'bio' in user_data:
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": user_data['email'], "password": user_data['password']}
            )
            token = login_response.json()['access_token']
            
            profile_data = {
                "bio": user_data.get('bio'),
                "expertise": user_data.get('expertise'),
                "interests": user_data.get('interests')
            }
            
            requests.patch(
                f"{BASE_URL}/users/{user['id']}",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"✅ Profile updated for {user_data['name']}")
        
        return user
    else:
        print(f"❌ Failed to register {user_data['name']}: {response.text}")
        return None

def login_user(email, password):
    """Login and return token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def create_sample_paper(author_token, title, abstract):
    """Create a sample paper (without actual PDF)"""
    print(f"Creating paper: {title}...")
    
    # Note: This is a simplified version without actual file upload
    # In real usage, you'd need to upload an actual PDF file
    print(f"⚠️  Skipping paper creation (requires actual PDF file)")
    print(f"   Use the web interface to upload papers with PDFs")

def main():
    print("=" * 60)
    print("🌱 Seeding Database with Sample Data")
    print("=" * 60)
    print()
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Backend is not responding. Make sure it's running at http://localhost:8000")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running at http://localhost:8000")
        return
    
    print("✅ Backend is running")
    print()
    
    # Register all users
    registered_users = {}
    for user_data in users:
        user = register_user(user_data)
        if user:
            registered_users[user_data['email']] = user
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("✅ Database seeded successfully!")
    print("=" * 60)
    print()
    print("📝 Test Accounts Created:")
    print()
    print("👤 Author Account:")
    print("   Email: alice@research.edu")
    print("   Password: password123")
    print()
    print("👤 Reviewer Account 1:")
    print("   Email: bob@review.edu")
    print("   Password: password123")
    print()
    print("👤 Reviewer Account 2:")
    print("   Email: carol@review.edu")
    print("   Password: password123")
    print()
    print("👤 Admin Account:")
    print("   Email: admin@system.com")
    print("   Password: admin123")
    print()
    print("🚀 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Login with any of the accounts above")
    print("3. As author: Upload papers")
    print("4. As admin: Assign reviewers to papers")
    print("5. As reviewer: Submit reviews and earn tokens!")
    print()

if __name__ == "__main__":
    main()
