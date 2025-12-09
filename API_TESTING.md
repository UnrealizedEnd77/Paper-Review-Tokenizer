# 🧪 API Testing Guide

Complete guide to test all API endpoints using the interactive documentation.

## Access Interactive API Docs

1. Start the backend server
2. Visit: http://localhost:8000/docs

## 🔐 Authentication Flow

### 1. Register a New User

**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
  "email": "testuser@example.com",
  "name": "Test User",
  "affiliation": "Test University",
  "role": "author",
  "password": "password123"
}
```

**Response**: Returns user object with ID

### 2. Login

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "testuser@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Important**: Copy the `access_token` value!

### 3. Authorize in Swagger UI

1. Click the green "Authorize" button at the top
2. Paste your token in the "Value" field
3. Click "Authorize"
4. Click "Close"

Now all subsequent requests will include your token!

## 📄 Paper Management APIs

### Upload Paper (Requires Author Role)

**Endpoint**: `POST /papers`

**Form Data**:
- `title`: "Machine Learning in Healthcare"
- `abstract`: "This paper explores..."
- `keywords`: "ML, Healthcare, AI"
- `category`: "Computer Science"
- `domain`: "Healthcare"
- `file`: [Choose a PDF file]

### Get Paper Details

**Endpoint**: `GET /papers/{paper_id}`

Example: `GET /papers/1`

### List All Papers

**Endpoint**: `GET /papers`

**Query Parameters**:
- `author_id`: Filter by author
- `status`: Filter by status (pending/under_review/reviewed)

### Download Paper

**Endpoint**: `GET /papers/{paper_id}/download`

Example: `GET /papers/1/download`

## ✍️ Review Workflow APIs

### Create Assignment (Admin Only)

**Endpoint**: `POST /assignments`

**Request Body**:
```json
{
  "paper_id": 1,
  "reviewer_id": 2,
  "deadline": "2024-12-31T23:59:59"
}
```

### List Assignments

**Endpoint**: `GET /assignments`

**Query Parameters**:
- `reviewer_id`: Filter by reviewer
- `paper_id`: Filter by paper

### Submit Review (Requires Reviewer Role)

**Endpoint**: `POST /reviews`

**Request Body**:
```json
{
  "paper_id": 1,
  "review_text": "This paper presents excellent research with clear methodology...",
  "rating": 4.5
}
```

### Get Review Details

**Endpoint**: `GET /reviews/{review_id}`

Example: `GET /reviews/1`

### List Reviews

**Endpoint**: `GET /reviews`

**Query Parameters**:
- `paper_id`: Get all reviews for a paper
- `reviewer_id`: Get all reviews by a reviewer

### Add Review Feedback (Author Only)

**Endpoint**: `POST /reviews/{review_id}/feedback`

**Request Body**:
```json
{
  "author_feedback_rating": 5.0,
  "author_feedback_text": "Very helpful review, thank you!"
}
```

## 🏆 Token & Leaderboard APIs

### Award Token Manually (Admin Only)

**Endpoint**: `POST /tokens/award`

**Request Body**:
```json
{
  "user_id": 2,
  "token_id": 1,
  "reason": "Outstanding contribution"
}
```

### Get User Tokens

**Endpoint**: `GET /users/{user_id}/tokens`

Example: `GET /users/2/tokens`

### Get Leaderboard

**Endpoint**: `GET /leaderboard`

**Query Parameters**:
- `limit`: Number of entries (default: 100)

### List All Achievements

**Endpoint**: `GET /achievements`

Returns all available token types.

## 📜 Proof & Audit APIs

### Get Review Proof

**Endpoint**: `GET /proofs/{review_id}`

Example: `GET /proofs/1`

Returns cryptographic proof of review.

### Generate Proof

**Endpoint**: `POST /proofs/generate`

**Query Parameters**:
- `review_id`: ID of the review

### Get Audit Logs (Admin Only)

**Endpoint**: `GET /audit/logs`

**Query Parameters**:
- `limit`: Number of logs to retrieve

### Get Paper Hash

**Endpoint**: `GET /integrity/hash/{paper_id}`

Example: `GET /integrity/hash/1`

Returns SHA-256 hash of paper file.

## 👤 User Management APIs

### Get Current User

**Endpoint**: `GET /auth/me`

Returns currently logged-in user info.

### Update Profile

**Endpoint**: `PATCH /users/{user_id}`

**Request Body**:
```json
{
  "bio": "Experienced researcher in AI",
  "expertise": "Machine Learning, Deep Learning",
  "interests": "Computer Vision, NLP"
}
```

### Get User Profile

**Endpoint**: `GET /users/{user_id}`

Example: `GET /users/1`

### List Reviewers

**Endpoint**: `GET /reviewers`

**Query Parameters**:
- `expertise`: Filter by expertise keyword

## 🔄 Complete Test Workflow

### Step 1: Create Test Users

1. Register an author: `POST /auth/register`
   ```json
   {
     "email": "author@test.com",
     "name": "Test Author",
     "role": "author",
     "password": "pass123"
   }
   ```

2. Register a reviewer: `POST /auth/register`
   ```json
   {
     "email": "reviewer@test.com",
     "name": "Test Reviewer",
     "role": "reviewer",
     "password": "pass123"
   }
   ```

3. Register an admin: `POST /auth/register`
   ```json
   {
     "email": "admin@test.com",
     "name": "Test Admin",
     "role": "admin",
     "password": "pass123"
   }
   ```

### Step 2: Upload Paper (As Author)

1. Login as author
2. Get token and authorize
3. Upload paper: `POST /papers`

### Step 3: Assign Reviewer (As Admin)

1. Login as admin
2. Get token and authorize
3. Create assignment: `POST /assignments`
   ```json
   {
     "paper_id": 1,
     "reviewer_id": 2
   }
   ```

### Step 4: Submit Review (As Reviewer)

1. Login as reviewer
2. Get token and authorize
3. List assignments: `GET /assignments`
4. Download paper: `GET /papers/1/download`
5. Submit review: `POST /reviews`
   ```json
   {
     "paper_id": 1,
     "review_text": "Excellent research with clear methodology...",
     "rating": 4.5
   }
   ```

### Step 5: Provide Feedback (As Author)

1. Login as author
2. Get token and authorize
3. List reviews: `GET /reviews?paper_id=1`
4. Add feedback: `POST /reviews/1/feedback`
   ```json
   {
     "author_feedback_rating": 5.0,
     "author_feedback_text": "Very helpful!"
   }
   ```

### Step 6: Check Results

1. Get leaderboard: `GET /leaderboard`
2. Get reviewer tokens: `GET /users/2/tokens`
3. Get review proof: `GET /proofs/1`

## 🎯 Testing Scenarios

### Scenario 1: Token Earning
1. Submit 1 review → Check for "First Review" badge
2. Submit 10 reviews → Check for "Prolific Reviewer" badge
3. Get 5-star feedback → Check for "Highly Rated" achievement

### Scenario 2: Ranking System
1. Submit multiple reviews
2. Get various feedback ratings
3. Check leaderboard ranking changes
4. Verify ranking score calculations

### Scenario 3: Access Control
1. Try to upload paper as reviewer (should fail)
2. Try to review unassigned paper (should fail)
3. Try to access admin endpoints as regular user (should fail)

### Scenario 4: Proof Generation
1. Submit a review
2. Get proof: `GET /proofs/{review_id}`
3. Verify proof contains correct hash

## 🐛 Common Issues

### "Not authenticated"
- Make sure you clicked "Authorize" with your token
- Token might be expired (expires in 43200 minutes by default)

### "Not authorized"
- Check if you have the right role for the operation
- Authors can't submit reviews
- Reviewers can't upload papers
- Only admins can create assignments

### "Paper not found"
- Use correct paper ID
- Papers are auto-incremented starting from 1

### "Review already exists"
- Each reviewer can only submit one review per paper

## 💡 Tips

1. **Use Try it Out**: Click "Try it out" button to test endpoints
2. **Check Responses**: Always review the response to understand the data structure
3. **Copy IDs**: Keep track of user IDs, paper IDs, review IDs for testing
4. **Test Error Cases**: Try invalid data to see error handling
5. **Use Different Roles**: Test with author, reviewer, and admin accounts

## 📊 Expected Responses

### Success
- Status Code: 200 (GET) or 201 (POST)
- JSON response with data

### Validation Error
- Status Code: 422
- Details about what's wrong with the request

### Authentication Error
- Status Code: 401
- Need to login or token is invalid

### Authorization Error
- Status Code: 403
- User doesn't have permission

### Not Found
- Status Code: 404
- Resource doesn't exist

---

Happy Testing! 🚀
