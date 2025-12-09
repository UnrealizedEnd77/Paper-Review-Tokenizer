# Research Paper Review Tokenizer

A comprehensive web platform for incentivized peer review of research papers using a tokenization system.

## 🌟 Features

### For Authors
- 📤 Upload research papers (PDF format)
- 📊 Track submission status
- 💬 View and rate reviews
- 📈 Monitor paper progress

### For Reviewers
- ✍️ Submit detailed reviews
- 🏆 Earn tokens and badges
- 📊 Climb the leaderboard
- 🎯 Build reputation through quality reviews
- 📜 Generate verifiable review proofs

### Token System
- 🌟 **Badges**: First Review, Prolific Reviewer, Expert Reviewer
- ⭐ **Achievements**: Highly Rated, Speed Reviewer
- 🔓 **Access Tokens**: Premium research paper access
- 📊 **Leaderboard Rankings**: Bronze, Silver, Gold, Platinum levels

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLite**: Lightweight database
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation
- **JWT**: Secure authentication

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript (Vanilla)**: No framework dependencies
- **Responsive Design**: Works on all devices

## 📁 Project Structure

```
Tokenizer/
├── backend/
│   ├── main.py           # FastAPI application & API endpoints
│   ├── database.py       # Database models & setup
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # Authentication utilities
│   ├── config.py         # Configuration settings
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment variables
└── frontend/
    ├── index.html        # Main HTML file
    ├── styles.css        # Styling
    └── app.js           # JavaScript logic
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- A modern web browser

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**
```bash
python main.py
```

The backend will start at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Serve the frontend**

You can use any static file server. Here are some options:

**Option 1: Python's built-in server**
```bash
python -m http.server 3000
```

**Option 2: Using Node.js http-server (if you have Node installed)**
```bash
npx http-server -p 3000
```

**Option 3: VS Code Live Server extension**
- Install "Live Server" extension in VS Code
- Right-click on `index.html` and select "Open with Live Server"

The frontend will be available at `http://localhost:3000`

## 📖 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 🎮 Usage Guide

### Getting Started

1. **Register an Account**
   - Open the frontend in your browser
   - Click "Register"
   - Choose your role: Author or Reviewer
   - Fill in your details

2. **As an Author**
   - Login to your dashboard
   - Click "Upload Paper"
   - Fill in paper details and upload PDF
   - Wait for reviewers to be assigned
   - View reviews and provide feedback

3. **As a Reviewer**
   - Login to your dashboard
   - View assigned papers
   - Download and read papers
   - Submit detailed reviews
   - Earn tokens and climb the leaderboard!

### Token System

**How to Earn Tokens:**
- Complete your first review → "First Review" badge
- Complete 10 reviews → "Prolific Reviewer" badge
- Complete 50 reviews → "Expert Reviewer" badge
- Get 5-star feedback → "Highly Rated" achievement
- Reach 100 ranking points → "Premium Access" token

**Ranking Points:**
- Complete a review: +10 points
- Get 5-star feedback: +10 bonus points
- Get 4-star feedback: +5 bonus points
- Get 3-star feedback: 0 bonus points
- Get 2-star feedback: -5 points
- Get 1-star feedback: -10 points

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Cryptographic review proofs (SHA-256)
- File integrity verification
- Audit logging

## 🎨 Design Features

- Vibrant gradient color scheme
- Dark mode interface
- Responsive layout
- Smooth animations
- Intuitive navigation
- Role-based dashboards

## 🔧 Configuration

Edit `backend/.env` to customize:

```env
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
DATABASE_URL=sqlite:///./research_tokenizer.db
```

## 📝 Default User Roles

- **Author**: Can upload papers, view reviews, provide feedback
- **Reviewer**: Can review assigned papers, earn tokens, view leaderboard
- **Admin**: Can manage all aspects (assign reviewers, access audit logs)

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

**Frontend can't connect to backend:**
- Verify backend is running at `http://localhost:8000`
- Check browser console for CORS errors
- Ensure API_BASE_URL in `app.js` matches your backend URL

**Database errors:**
- Delete `research_tokenizer.db` and restart the backend to recreate

## 📊 Database Schema

The platform uses SQLite with the following main tables:
- **users**: User accounts and profiles
- **papers**: Research paper submissions
- **review_assignments**: Reviewer-paper assignments
- **reviews**: Review submissions
- **tokens**: Token types/achievements
- **user_tokens**: User's earned tokens
- **leaderboard_stats**: Reviewer rankings
- **review_proofs**: Cryptographic proof of reviews
- **audit_logs**: System activity logs

## 🤝 Contributing

This is a demonstration project. Feel free to fork and customize for your needs!

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🎯 Future Enhancements

Potential features to add:
- Email notifications
- Advanced search and filtering
- Paper versioning
- Multi-round reviews
- Anonymous review option
- Integration with ORCID
- Export reviews as PDF
- Analytics dashboard
- API rate limiting
- WebSocket for real-time updates

## 💡 Tips

- **For Testing**: Create both an author and reviewer account to see all features
- **Best Practice**: Use meaningful paper titles and detailed reviews
- **Security**: Change the SECRET_KEY in .env for production use
- **Performance**: For production, consider using PostgreSQL instead of SQLite

---

Built with ❤️ using FastAPI and Vanilla JavaScript
