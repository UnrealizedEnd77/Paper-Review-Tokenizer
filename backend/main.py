from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
import shutil
import hashlib
import json

from database import get_db, init_db
from database import User, Paper, Review, ReviewAssignment, UserToken, LeaderboardStats, AuditLog, ReviewProof
from database import Token as TokenModel
from schemas import *
from auth import get_password_hash, verify_password, create_access_token, get_current_user
import config

app = FastAPI(title="Research Paper Review Tokenizer")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Create upload directory
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    # Initialize default tokens
    db = next(get_db())
    initialize_default_tokens(db)

def initialize_default_tokens(db: Session):
    """Create default token types if they don't exist"""
    default_tokens = [
        {"name": "First Review", "description": "Completed your first review", "type": "badge", "icon": "🌟", "criteria": "Complete 1 review"},
        {"name": "Prolific Reviewer", "description": "Completed 10 reviews", "type": "badge", "icon": "🏆", "criteria": "Complete 10 reviews"},
        {"name": "Expert Reviewer", "description": "Completed 50 reviews", "type": "badge", "icon": "💎", "criteria": "Complete 50 reviews"},
        {"name": "Highly Rated", "description": "Received 5-star feedback", "type": "achievement", "icon": "⭐", "criteria": "Get 5-star author feedback"},
        {"name": "Speed Reviewer", "description": "Completed review within 24 hours", "type": "achievement", "icon": "⚡", "criteria": "Complete review in 24 hours"},
        {"name": "Premium Access", "description": "Access to premium research papers", "type": "access", "icon": "🔓", "criteria": "Earn 100 ranking points"},
    ]
    
    for token_data in default_tokens:
        existing = db.query(TokenModel).filter(TokenModel.name == token_data["name"]).first()
        if not existing:
            token = TokenModel(**token_data)
            db.add(token)
    
    db.commit()

# ==================== Authentication APIs ====================

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        affiliation=user.affiliation,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create leaderboard stats for reviewers
    if user.role == "reviewer":
        stats = LeaderboardStats(user_id=db_user.id)
        db.add(stats)
        db.commit()
    
    # Log the action
    log = AuditLog(user_id=db_user.id, action="register", resource_type="user", resource_id=db_user.id)
    db.add(log)
    db.commit()
    
    return db_user

@app.post("/auth/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    # Log the action
    log = AuditLog(user_id=user.id, action="login", resource_type="user", resource_id=user.id)
    db.add(log)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current logged-in user information"""
    return current_user

@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.bio is not None:
        user.bio = user_update.bio
    if user_update.expertise is not None:
        user.expertise = user_update.expertise
    if user_update.interests is not None:
        user.interests = user_update.interests
    
    db.commit()
    db.refresh(user)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="update_profile", resource_type="user", resource_id=user_id)
    db.add(log)
    db.commit()
    
    return user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/reviewers", response_model=List[UserResponse])
def list_reviewers(expertise: Optional[str] = None, db: Session = Depends(get_db)):
    """List all reviewers, optionally filtered by expertise"""
    query = db.query(User).filter(User.role == "reviewer")
    
    if expertise:
        query = query.filter(User.expertise.contains(expertise))
    
    return query.all()

# ==================== Paper Management APIs ====================

@app.post("/papers", response_model=PaperResponse)
async def create_paper(
    title: str = Form(...),
    abstract: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    domain: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new paper"""
    if current_user.role not in ["author", "admin"]:
        raise HTTPException(status_code=403, detail="Only authors can upload papers")
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{datetime.utcnow().timestamp()}{file_extension}"
    file_path = os.path.join(config.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create paper record
    paper = Paper(
        author_id=current_user.id,
        title=title,
        abstract=abstract,
        keywords=keywords,
        category=category,
        domain=domain,
        file_path=file_path,
        status="pending"
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="upload_paper", resource_type="paper", resource_id=paper.id)
    db.add(log)
    db.commit()
    
    return paper

@app.get("/papers/{paper_id}", response_model=PaperResponse)
def get_paper(paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get paper details"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@app.get("/papers", response_model=List[PaperResponse])
def list_papers(
    author_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List papers with optional filters"""
    query = db.query(Paper)
    
    # If not admin, only show own papers for authors
    if current_user.role == "author":
        query = query.filter(Paper.author_id == current_user.id)
    elif author_id:
        query = query.filter(Paper.author_id == author_id)
    
    if status:
        query = query.filter(Paper.status == status)
    
    return query.all()

@app.patch("/papers/{paper_id}", response_model=PaperResponse)
def update_paper(
    paper_id: int,
    paper_update: PaperBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update paper information"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if current_user.id != paper.author_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this paper")
    
    paper.title = paper_update.title
    paper.abstract = paper_update.abstract
    paper.keywords = paper_update.keywords
    paper.category = paper_update.category
    paper.domain = paper_update.domain
    paper.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(paper)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="update_paper", resource_type="paper", resource_id=paper_id)
    db.add(log)
    db.commit()
    
    return paper

@app.get("/papers/{paper_id}/download")
def download_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download paper PDF"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check if user has access (author, assigned reviewer, or admin)
    is_author = current_user.id == paper.author_id
    is_assigned_reviewer = db.query(ReviewAssignment).filter(
        ReviewAssignment.paper_id == paper_id,
        ReviewAssignment.reviewer_id == current_user.id
    ).first() is not None
    is_admin = current_user.role == "admin"
    
    if not (is_author or is_assigned_reviewer or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to download this paper")
    
    if not os.path.exists(paper.file_path):
        raise HTTPException(status_code=404, detail="Paper file not found")
    
    return FileResponse(paper.file_path, media_type="application/pdf", filename=f"{paper.title}.pdf")

# ==================== Review Workflow APIs ====================

@app.post("/assignments", response_model=ReviewAssignmentResponse)
def create_assignment(
    assignment: ReviewAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a reviewer to a paper"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create assignments")
    
    # Check if paper exists
    paper = db.query(Paper).filter(Paper.id == assignment.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check if reviewer exists and has reviewer role
    reviewer = db.query(User).filter(User.id == assignment.reviewer_id).first()
    if not reviewer or reviewer.role != "reviewer":
        raise HTTPException(status_code=404, detail="Reviewer not found")
    
    # Check if already assigned
    existing = db.query(ReviewAssignment).filter(
        ReviewAssignment.paper_id == assignment.paper_id,
        ReviewAssignment.reviewer_id == assignment.reviewer_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reviewer already assigned to this paper")
    
    # Create assignment
    db_assignment = ReviewAssignment(
        paper_id=assignment.paper_id,
        reviewer_id=assignment.reviewer_id,
        deadline=assignment.deadline,
        status="assigned"
    )
    db.add(db_assignment)
    

    @app.post("/papers/{paper_id}/assign")
    def assign_reviewer_to_paper(
        paper_id: int,
        assignment: ReviewAssignmentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Assign a reviewer to a paper (author or admin only)"""
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Allow author or admin to assign
        if current_user.id != paper.author_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if reviewer exists
        reviewer = db.query(User).filter(User.id == assignment.reviewer_id).first()
        if not reviewer or reviewer.role != "reviewer":
            raise HTTPException(status_code=404, detail="Reviewer not found")
        
        # Check if already assigned
        existing = db.query(ReviewAssignment).filter(
            ReviewAssignment.paper_id == paper_id,
            ReviewAssignment.reviewer_id == assignment.reviewer_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Reviewer already assigned")
        
        # Create assignment
        db_assignment = ReviewAssignment(
            paper_id=paper_id,
            reviewer_id=assignment.reviewer_id,
            deadline=assignment.deadline,
            status="assigned"
        )
        db.add(db_assignment)
        paper.status = "under_review"
        db.commit()
        db.refresh(db_assignment)
        
        # Log the action
        log = AuditLog(user_id=current_user.id, action="assign_reviewer", resource_type="assignment", resource_id=db_assignment.id)
        db.add(log)
        db.commit()
        
        return {"message": "Reviewer assigned successfully", "assignment_id": db_assignment.id}

    
    # Update paper status
    paper.status = "under_review"
    
    db.commit()
    db.refresh(db_assignment)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="assign_reviewer", resource_type="assignment", resource_id=db_assignment.id)
    db.add(log)
    db.commit()
    
    return db_assignment

@app.get("/assignments", response_model=List[ReviewAssignmentResponse])
def list_assignments(
    reviewer_id: Optional[int] = None,
    paper_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List review assignments"""
    query = db.query(ReviewAssignment)
    
    # If reviewer, only show own assignments
    if current_user.role == "reviewer":
        query = query.filter(ReviewAssignment.reviewer_id == current_user.id)
    elif reviewer_id:
        query = query.filter(ReviewAssignment.reviewer_id == reviewer_id)
    
    if paper_id:
        query = query.filter(ReviewAssignment.paper_id == paper_id)
    
    return query.all()

@app.post("/reviews", response_model=ReviewResponse)
def submit_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review for a paper"""
    if current_user.role != "reviewer":
        raise HTTPException(status_code=403, detail="Only reviewers can submit reviews")
    
    # Check if paper exists
    paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check if reviewer is assigned to this paper
    assignment = db.query(ReviewAssignment).filter(
        ReviewAssignment.paper_id == review.paper_id,
        ReviewAssignment.reviewer_id == current_user.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=403, detail="You are not assigned to review this paper")
    
    # Create review
    db_review = Review(
        paper_id=review.paper_id,
        reviewer_id=current_user.id,
        assignment_id=assignment.id,
        review_text=review.review_text,
        rating=review.rating
    )
    db.add(db_review)
    
    # Update assignment status
    assignment.status = "completed"
    
    # Update leaderboard stats
    stats = db.query(LeaderboardStats).filter(LeaderboardStats.user_id == current_user.id).first()
    if stats:
        stats.total_reviews += 1
        stats.ranking_score += 10  # Base points for completing a review
        
        # Update level based on total reviews
        if stats.total_reviews >= 50:
            stats.level = "platinum"
        elif stats.total_reviews >= 20:
            stats.level = "gold"
        elif stats.total_reviews >= 10:
            stats.level = "silver"
    
    db.commit()
    db.refresh(db_review)
    
    # Award tokens based on milestones
    award_review_tokens(current_user.id, db)
    
    # Generate proof for this review
    generate_review_proof(db_review.id, db)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="submit_review", resource_type="review", resource_id=db_review.id)
    db.add(log)
    db.commit()
    
    return db_review

@app.get("/reviews", response_model=List[ReviewResponse])
def list_reviews(
    paper_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List reviews"""
    query = db.query(Review)
    
    if paper_id:
        # Check if user has access to this paper's reviews
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Only author of paper or admin can see all reviews
        if current_user.id != paper.author_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these reviews")
        
        query = query.filter(Review.paper_id == paper_id)
    
    if reviewer_id:
        query = query.filter(Review.reviewer_id == reviewer_id)
    
    # If reviewer, only show own reviews
    if current_user.role == "reviewer":
        query = query.filter(Review.reviewer_id == current_user.id)
    
    return query.all()

@app.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get review details"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check authorization
    paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
    if current_user.id != review.reviewer_id and current_user.id != paper.author_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this review")
    
    return review

@app.post("/reviews/{review_id}/feedback", response_model=ReviewResponse)
def add_review_feedback(
    review_id: int,
    feedback: ReviewFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Author adds feedback/rating to a review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if current user is the author of the paper
    paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
    if current_user.id != paper.author_id:
        raise HTTPException(status_code=403, detail="Only the paper author can provide feedback")
    
    review.author_feedback_rating = feedback.author_feedback_rating
    review.author_feedback_text = feedback.author_feedback_text
    
    # Update reviewer's ranking score based on feedback
    if feedback.author_feedback_rating:
        stats = db.query(LeaderboardStats).filter(LeaderboardStats.user_id == review.reviewer_id).first()
        if stats:
            # Add bonus points for good feedback (5 stars = 10 bonus points)
            bonus = (feedback.author_feedback_rating - 3) * 5  # -10 to +10 points
            stats.ranking_score += bonus
            
            # Award highly rated token if 5 stars
            if feedback.author_feedback_rating >= 5.0:
                highly_rated_token = db.query(TokenModel).filter(TokenModel.name == "Highly Rated").first()
                if highly_rated_token:
                    existing_award = db.query(UserToken).filter(
                        UserToken.user_id == review.reviewer_id,
                        UserToken.token_id == highly_rated_token.id
                    ).first()
                    if not existing_award:
                        user_token = UserToken(
                            user_id=review.reviewer_id,
                            token_id=highly_rated_token.id,
                            reason=f"Received 5-star feedback on review #{review.id}"
                        )
                        db.add(user_token)
                        stats.total_tokens += 1
    
    db.commit()
    db.refresh(review)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="provide_review_feedback", resource_type="review", resource_id=review_id)
    db.add(log)
    db.commit()
    
    return review

# ==================== Token & Leaderboard APIs ====================

def award_review_tokens(user_id: int, db: Session):
    """Award tokens based on review milestones"""
    stats = db.query(LeaderboardStats).filter(LeaderboardStats.user_id == user_id).first()
    if not stats:
        return
    
    milestones = [
        (1, "First Review"),
        (10, "Prolific Reviewer"),
        (50, "Expert Reviewer"),
    ]
    
    for count, token_name in milestones:
        if stats.total_reviews == count:
            token = db.query(TokenModel).filter(TokenModel.name == token_name).first()
            if token:
                # Check if already awarded
                existing = db.query(UserToken).filter(
                    UserToken.user_id == user_id,
                    UserToken.token_id == token.id
                ).first()
                
                if not existing:
                    user_token = UserToken(
                        user_id=user_id,
                        token_id=token.id,
                        reason=f"Completed {count} review(s)"
                    )
                    db.add(user_token)
                    stats.total_tokens += 1
    
    # Premium access for high ranking score
    if stats.ranking_score >= 100:
        premium_token = db.query(TokenModel).filter(TokenModel.name == "Premium Access").first()
        if premium_token:
            existing = db.query(UserToken).filter(
                UserToken.user_id == user_id,
                UserToken.token_id == premium_token.id
            ).first()
            if not existing:
                user_token = UserToken(
                    user_id=user_id,
                    token_id=premium_token.id,
                    reason="Achieved 100 ranking points"
                )
                db.add(user_token)
                stats.total_tokens += 1
    
    db.commit()

@app.post("/tokens/award", response_model=UserTokenResponse)
def award_token_manually(
    award: AwardTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually award a token to a user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manually award tokens")
    
    # Check if token exists
    token = db.query(TokenModel).filter(TokenModel.id == award.token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Check if user exists
    user = db.query(User).filter(User.id == award.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create user token
    user_token = UserToken(
        user_id=award.user_id,
        token_id=award.token_id,
        reason=award.reason or "Manually awarded by admin"
    )
    db.add(user_token)
    
    # Update stats
    stats = db.query(LeaderboardStats).filter(LeaderboardStats.user_id == award.user_id).first()
    if stats:
        stats.total_tokens += 1
    
    db.commit()
    db.refresh(user_token)
    
    # Log the action
    log = AuditLog(user_id=current_user.id, action="award_token", resource_type="user_token", resource_id=user_token.id)
    db.add(log)
    db.commit()
    
    return user_token

@app.get("/users/{user_id}/tokens", response_model=List[UserTokenResponse])
def get_user_tokens(user_id: int, db: Session = Depends(get_db)):
    """Get all tokens earned by a user"""
    user_tokens = db.query(UserToken).filter(UserToken.user_id == user_id).all()
    return user_tokens

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(limit: int = 100, db: Session = Depends(get_db)):
    """Get reviewer leaderboard"""
    stats = db.query(LeaderboardStats, User).join(User).order_by(
        LeaderboardStats.ranking_score.desc()
    ).limit(limit).all()
    
    result = []
    for stat, user in stats:
        result.append({
            "user_id": user.id,
            "name": user.name,
            "total_reviews": stat.total_reviews,
            "total_tokens": stat.total_tokens,
            "ranking_score": stat.ranking_score,
            "level": stat.level
        })
    
    return result

@app.get("/achievements", response_model=List[TokenTypeResponse])
def list_achievements(db: Session = Depends(get_db)):
    """List all available token types/achievements"""
    tokens = db.query(TokenModel).all()
    return tokens

# ==================== Proof & Audit APIs ====================

def generate_review_proof(review_id: int, db: Session):
    """Generate cryptographic proof for a review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return
    
    # Create proof data
    proof_data = {
        "review_id": review.id,
        "paper_id": review.paper_id,
        "reviewer_id": review.reviewer_id,
        "timestamp": review.timestamp.isoformat(),
        "rating": review.rating,
        "review_text_hash": hashlib.sha256(review.review_text.encode()).hexdigest()
    }
    
    proof_json = json.dumps(proof_data, sort_keys=True)
    proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
    
    # Store proof
    proof = ReviewProof(
        review_id=review.id,
        proof_hash=proof_hash,
        proof_data=proof_json
    )
    db.add(proof)
    db.commit()

@app.get("/proofs/{review_id}", response_model=ProofResponse)
def get_review_proof(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get proof of review for verification"""
    proof = db.query(ReviewProof).filter(ReviewProof.review_id == review_id).first()
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    # Check if user has access (reviewer who wrote it or admin)
    review = db.query(Review).filter(Review.id == review_id).first()
    if current_user.id != review.reviewer_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this proof")
    
    return proof

@app.post("/proofs/generate")
def generate_proof(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate new proof for a review (if not exists)"""
    # Check if proof already exists
    existing_proof = db.query(ReviewProof).filter(ReviewProof.review_id == review_id).first()
    if existing_proof:
        return {"message": "Proof already exists", "proof_hash": existing_proof.proof_hash}
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if current_user.id != review.reviewer_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    generate_review_proof(review_id, db)
    
    proof = db.query(ReviewProof).filter(ReviewProof.review_id == review_id).first()
    return {"message": "Proof generated successfully", "proof_hash": proof.proof_hash}

@app.get("/audit/logs")
def get_audit_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can access audit logs")
    
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs

@app.get("/integrity/hash/{paper_id}")
def get_paper_hash(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hash of paper file for integrity verification"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check authorization
    is_author = current_user.id == paper.author_id
    is_assigned_reviewer = db.query(ReviewAssignment).filter(
        ReviewAssignment.paper_id == paper_id,
        ReviewAssignment.reviewer_id == current_user.id
    ).first() is not None
    is_admin = current_user.role == "admin"
    
    if not (is_author or is_assigned_reviewer or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not os.path.exists(paper.file_path):
        raise HTTPException(status_code=404, detail="Paper file not found")
    
    # Calculate SHA256 hash
    sha256_hash = hashlib.sha256()
    with open(paper.file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return {
        "paper_id": paper_id,
        "file_hash": sha256_hash.hexdigest(),
        "algorithm": "SHA256"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
