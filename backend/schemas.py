from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    affiliation: Optional[str] = None
    role: str  # author/reviewer/admin

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    bio: Optional[str] = None
    expertise: Optional[str] = None
    interests: Optional[str] = None

class UserResponse(UserBase):
    id: int
    bio: Optional[str] = None
    expertise: Optional[str] = None
    interests: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Paper Schemas
class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    category: Optional[str] = None
    domain: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class PaperResponse(PaperBase):
    id: int
    author_id: int
    status: str
    file_path: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Review Assignment Schemas
class ReviewAssignmentCreate(BaseModel):
    paper_id: int
    reviewer_id: int
    deadline: Optional[datetime] = None

class ReviewAssignmentResponse(BaseModel):
    id: int
    paper_id: int
    reviewer_id: int
    status: str
    deadline: Optional[datetime]
    assigned_at: datetime
    
    class Config:
        from_attributes = True

# Review Schemas
class ReviewCreate(BaseModel):
    paper_id: int
    review_text: str
    rating: Optional[float] = None

class ReviewFeedbackCreate(BaseModel):
    author_feedback_rating: Optional[float] = None
    author_feedback_text: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    paper_id: int
    reviewer_id: int
    review_text: str
    rating: Optional[float]
    timestamp: datetime
    author_feedback_rating: Optional[float] = None
    author_feedback_text: Optional[str] = None
    
    class Config:
        from_attributes = True

# Token Schemas
class TokenTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    icon: Optional[str] = None
    criteria: Optional[str] = None

class TokenTypeResponse(TokenTypeBase):
    id: int
    
    class Config:
        from_attributes = True

class AwardTokenRequest(BaseModel):
    user_id: int
    token_id: int
    reason: Optional[str] = None

class UserTokenResponse(BaseModel):
    id: int
    token_id: int
    earned_at: datetime
    reason: Optional[str]
    token: TokenTypeResponse
    
    class Config:
        from_attributes = True

# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    user_id: int
    name: str
    total_reviews: int
    total_tokens: int
    ranking_score: float
    level: str
    
    class Config:
        from_attributes = True

# Proof Schemas
class ProofResponse(BaseModel):
    id: int
    review_id: int
    proof_hash: str
    proof_data: str
    generated_at: datetime
    
    class Config:
        from_attributes = True
