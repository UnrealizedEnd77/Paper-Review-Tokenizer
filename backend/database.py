from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

# Create engine
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    affiliation = Column(String)
    role = Column(String, nullable=False)  # author/reviewer/admin
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Profile fields
    bio = Column(Text)
    expertise = Column(String)  # comma-separated
    interests = Column(String)  # comma-separated
    
    # Relationships
    papers = relationship("Paper", back_populates="author")
    review_assignments = relationship("ReviewAssignment", back_populates="reviewer")
    reviews = relationship("Review", back_populates="reviewer")
    tokens = relationship("UserToken", back_populates="user")
    leaderboard_stats = relationship("LeaderboardStats", back_populates="user", uselist=False)


class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(Text)
    file_path = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending/under_review/reviewed/completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    keywords = Column(String)  # comma-separated
    category = Column(String)
    domain = Column(String)
    
    # Relationships
    author = relationship("User", back_populates="papers")
    review_assignments = relationship("ReviewAssignment", back_populates="paper")
    reviews = relationship("Review", back_populates="paper")


class ReviewAssignment(Base):
    __tablename__ = "review_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="assigned")  # assigned/in_progress/completed
    deadline = Column(DateTime)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    paper = relationship("Paper", back_populates="review_assignments")
    reviewer = relationship("User", back_populates="review_assignments")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("review_assignments.id"))
    
    review_text = Column(Text, nullable=False)
    rating = Column(Float)  # optional 1-5 rating
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Author feedback
    author_feedback_rating = Column(Float)  # how useful was this review
    author_feedback_text = Column(Text)
    
    # Relationships
    paper = relationship("Paper", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    type = Column(String)  # badge/achievement/access
    icon = Column(String)  # emoji or icon name
    criteria = Column(String)  # what needs to be done to earn this


class UserToken(Base):
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String)  # why was this awarded
    
    # Relationships
    user = relationship("User", back_populates="tokens")
    token = relationship("Token")


class LeaderboardStats(Base):
    __tablename__ = "leaderboard_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_reviews = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    ranking_score = Column(Float, default=0.0)
    level = Column(String, default="bronze")  # bronze/silver/gold/platinum
    
    # Relationships
    user = relationship("User", back_populates="leaderboard_stats")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(Integer)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ReviewProof(Base):
    __tablename__ = "review_proofs"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    proof_hash = Column(String, nullable=False, unique=True)
    proof_data = Column(Text, nullable=False)  # JSON string
    generated_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)
