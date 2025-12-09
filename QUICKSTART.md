# 🚀 Quick Start Guide

Get the Research Paper Review Tokenizer up and running in 5 minutes!

## Step 1: Start the Backend

Open a terminal in the project directory and run:

### On Windows:
```bash
start-backend.bat
```

### On Mac/Linux:
```bash
chmod +x start-backend.sh
./start-backend.sh
```

The backend will:
- Create a virtual environment
- Install all dependencies
- Create the database
- Start the server at http://localhost:8000

✅ **Verification**: Visit http://localhost:8000/docs to see the API documentation

## Step 2: Start the Frontend

Open a **NEW** terminal in the project directory and run:

### On Windows:
```bash
start-frontend.bat
```

### On Mac/Linux:
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

The frontend will start at http://localhost:3000

✅ **Verification**: Visit http://localhost:3000 to see the login page

## Step 3: Create Test Accounts

### Create an Author Account
1. Click "Register"
2. Fill in:
   - Name: `John Author`
   - Email: `author@test.com`
   - Role: **Author**
   - Password: `password123`
3. Click "Register"

### Create a Reviewer Account
1. Click "Register" (or refresh the page)
2. Fill in:
   - Name: `Jane Reviewer`
   - Email: `reviewer@test.com`
   - Role: **Reviewer**
   - Password: `password123`
3. Click "Register"

## Step 4: Test the System

### As Author (author@test.com / password123)
1. Login
2. Click "Upload Paper"
3. Fill in:
   - Title: "Machine Learning in Healthcare"
   - Abstract: "This paper explores..."
   - Upload a PDF (any PDF file)
4. Click "Upload Paper"
5. View your paper in the Papers section

### As Admin (Manual Database Entry Required)
To assign reviewers, you need admin access. For testing:

**Option 1: Use API directly**
Visit http://localhost:8000/docs and use the `/assignments` endpoint

**Option 2: Create admin account via database**
```bash
# In backend directory
sqlite3 research_tokenizer.db
UPDATE users SET role='admin' WHERE email='author@test.com';
.quit
```

Then login as author@test.com and use admin features.

### As Reviewer (reviewer@test.com / password123)
1. Login
2. Once assigned a paper, you'll see it in "Reviews" section
3. Click "Submit Review"
4. Write your review
5. Submit to earn tokens!

## 🎯 What to Explore

### Author Features
- ✅ Upload multiple papers
- ✅ Track paper status
- ✅ View reviews
- ✅ Rate review quality
- ✅ Download papers

### Reviewer Features
- ✅ View assigned papers
- ✅ Submit reviews with ratings
- ✅ Earn tokens and badges
- ✅ Check leaderboard ranking
- ✅ Build your profile

### Token System
- 🌟 Complete 1 review → First Review badge
- 🏆 Complete 10 reviews → Prolific Reviewer badge
- 💎 Complete 50 reviews → Expert Reviewer badge
- ⭐ Get 5-star feedback → Highly Rated achievement
- 🔓 Reach 100 points → Premium Access token

## 🔧 Manual Setup (If Scripts Don't Work)

### Backend Manual Setup
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Frontend Manual Setup
```bash
cd frontend
python -m http.server 3000
```

## 🐛 Troubleshooting

### "Module not found" error
```bash
cd backend
pip install -r requirements.txt
```

### "Port already in use"
**Backend**: Change port in `main.py` (last line)
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed from 8000
```

**Frontend**: Change port in start script
```bash
python -m http.server 3001  # Changed from 3000
```
Update `API_BASE_URL` in `frontend/app.js` if you change backend port.

### "Cannot connect to backend"
1. Make sure backend is running (http://localhost:8000/docs should work)
2. Check browser console for errors
3. Verify `API_BASE_URL` in `frontend/app.js` is correct

### Database locked error
Close any SQLite database viewers and restart the backend.

## 📱 Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 🎨 UI Features to Try

1. **Vibrant Dashboard**: See stats and quick actions
2. **Paper Cards**: Visual paper management
3. **Token Display**: Beautiful badge showcase
4. **Leaderboard**: Competitive rankings with color-coded levels
5. **Responsive Design**: Try on different screen sizes

## 💡 Pro Tips

1. **Create multiple accounts** to test different roles
2. **Use meaningful titles** for easier paper identification
3. **Write detailed reviews** to earn better author feedback
4. **Check the leaderboard** to see your ranking improve
5. **Explore the API docs** at /docs for advanced features

## 🎓 Test Scenario

Try this complete workflow:

1. **Author uploads paper** (author@test.com)
2. **Admin assigns reviewer** (via API /assignments endpoint)
3. **Reviewer downloads paper** (reviewer@test.com)
4. **Reviewer submits review**
5. **Author views review**
6. **Author rates review** (5 stars!)
7. **Reviewer earns tokens**
8. **Check leaderboard** for updated ranking

## 📞 Need Help?

- Check the main README.md for detailed documentation
- Review the API docs at http://localhost:8000/docs
- Examine the code in `backend/main.py` for API logic
- Check `frontend/app.js` for frontend implementation

---

🎉 **You're all set! Enjoy exploring the Research Paper Review Tokenizer!**
