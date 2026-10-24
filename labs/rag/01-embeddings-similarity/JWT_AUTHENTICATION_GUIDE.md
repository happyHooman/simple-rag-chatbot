# JWT Authentication Guide

## 🔐 How JWT Authentication Works

Your FAQ Chatbot uses **JWT (JSON Web Tokens)** for secure, stateless authentication.

### Token Structure

A JWT has 3 parts separated by dots (`.`):
```
HEADER.PAYLOAD.SIGNATURE
```

**Example:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJleHAiOjE3MzM2NjY0MDAsImlhdCI6MTczMzU4MDAwMH0.J0VX3rWUIART8y1mCztpJRgbF4vLYrefFGv5BsVfPZg
```

### Token Creation Process

1. **Payload** - Contains user info (`sub`), token type, expiration (`exp`), and issued time (`iat`)
2. **Signing** - Signed with your `JWT_SECRET_KEY` using HS256 algorithm
3. **Expiration** - Default 24 hours (configurable via `JWT_EXPIRATION_HOURS`)

---

## 🛠️ How to Generate JWT Tokens

### **Method 1: Quick Token Generator Script (Recommended)**

```bash
# Generate with defaults (admin user, 24 hours)
uv run python generate_token.py

# Generate custom user with custom expiration
uv run python generate_token.py my_username 48

# Generate short-lived token for testing
uv run python generate_token.py test_user 1
```

**Output:**
```
======================================================================
🔐 JWT TOKEN GENERATOR
======================================================================

👤 Subject: admin
⏰ Expires in: 24 hours

🎫 Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

📋 Use as header:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
======================================================================
```

### **Method 2: One-Line Python Command**

```bash
uv run python -c "from app.api.helpers.auth import create_access_token; print(create_access_token({'sub': 'admin'}))"
```

### **Method 3: From Docker Container**

First, rebuild your container to include the token generator:
```bash
docker compose up --build -d
```

Then generate a token:
```bash
docker exec faq_chatbot_app .venv/bin/python generate_token.py docker_user 24
```

### **Method 4: Interactive Script**

```bash
uv run python scripts/generate_token.py
```

Follow the prompts to enter:
- Username/subject (default: `admin`)
- Expiration hours (default: `24`)

---

## 🧪 Testing with JWT Tokens

### **1. Using cURL**

```bash
# First, generate a token
TOKEN=$(uv run python -c "from app.api.helpers.auth import create_access_token; print(create_access_token({'sub': 'admin'}))")

# Test protected endpoint
curl -X POST http://localhost:8000/ask-question \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_question": "How do I reset my password?"}'

# Generate embeddings
curl -X POST http://localhost:8000/generate-embeddings \
  -H "Authorization: Bearer $TOKEN"

# Check task status
curl -X GET http://localhost:8000/tasks/YOUR_TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### **2. Using Browser (Postman/Insomnia/Thunder Client)**

1. **Generate Token:**
   ```bash
   uv run python generate_token.py
   ```

2. **Copy the token** from the output

3. **In your API client:**
   - **URL:** `http://localhost:8000/ask-question`
   - **Method:** `POST`
   - **Headers:**
     - `Authorization`: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
     - `Content-Type`: `application/json`
   - **Body:**
     ```json
     {
       "user_question": "How do I reset my password?"
     }
     ```

### **3. Using Python Requests**

```python
import requests
from app.api.helpers.auth import create_access_token

# Generate token
token = create_access_token({"sub": "admin", "type": "access_token"})

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/ask-question",
    headers=headers,
    json={"user_question": "How do I reset my password?"}
)

print(response.json())
```

---

## 🔑 Environment Configuration

### Required Environment Variables

In your `.env` file:

```env
# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Security Best Practices

✅ **DO:**
- Use a strong, random secret key in production (min 32 characters)
- Rotate your secret key periodically
- Use HTTPS in production to prevent token interception
- Set appropriate expiration times (shorter for sensitive operations)

❌ **DON'T:**
- Commit your secret key to version control
- Use the default secret key in production
- Share tokens publicly
- Store tokens in localStorage (use httpOnly cookies in production)

---

## 🔍 Token Verification Process

When you send a request with a JWT token:

1. **Extract Token:** From `Authorization: Bearer <token>` header
2. **Verify Signature:** Ensures token hasn't been tampered with
3. **Check Expiration:** Ensures token is still valid
4. **Extract Payload:** Gets user info from token
5. **Grant Access:** If all checks pass

### Token Lifecycle

```mermaid
graph LR
    A[Generate Token] --> B[Send in Header]
    B --> C[API Receives]
    C --> D{Valid?}
    D -->|Yes| E[Process Request]
    D -->|No| F[Return 401]
    E --> G{Expired?}
    G -->|Yes| H[Generate New Token]
    G -->|No| I[Continue Using]
```

---

## 🐛 Troubleshooting

### Common Errors

#### 1. **"Invalid token"**
```json
{"error": "Invalid token"}
```
**Cause:** Token is malformed or signature doesn't match  
**Solution:** Generate a new token with the correct secret key

#### 2. **"Token has expired"**
```json
{"detail": "Token has expired"}
```
**Cause:** Token exceeded its expiration time  
**Solution:** Generate a new token

#### 3. **"Authentication required"**
```json
{"detail": "Authentication required"}
```
**Cause:** No Authorization header provided  
**Solution:** Add `Authorization: Bearer <token>` header

#### 4. **401 Unauthorized**
**Cause:** Token missing or invalid  
**Solution:**
```bash
# Regenerate token
uv run python generate_token.py

# Verify you're using it correctly
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/health
```

---

## 📊 Public vs Protected Endpoints

### Public Endpoints (No Auth Required)
- `GET /` - Root
- `GET /health` - Health check
- `GET /docs` - API documentation

### Protected Endpoints (Auth Required)
- `POST /ask-question` - Ask a question
- `POST /generate-embeddings` - Generate embeddings
- `POST /update-embeddings` - Update embeddings
- `GET /tasks/{task_id}` - Check task status

---

## 🎯 Quick Reference

```bash
# Generate token (default settings)
uv run python generate_token.py

# Generate token with custom expiration
uv run python generate_token.py admin 48

# Test authentication
TOKEN=$(uv run python -c "from app.api.helpers.auth import create_access_token; print(create_access_token({'sub': 'admin'}))")
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/ask-question -d '{"user_question":"test"}' -H "Content-Type: application/json"

# Decode token (for debugging)
echo "YOUR_TOKEN" | python -c "import jwt, sys; print(jwt.decode(sys.stdin.read().strip(), options={'verify_signature': False}))"
```

---

## 📚 Additional Resources

- **JWT.io** - Decode and inspect tokens: https://jwt.io
- **PyJWT Docs** - Library documentation: https://pyjwt.readthedocs.io
- **FastAPI Security** - Official guide: https://fastapi.tiangolo.com/tutorial/security/

---

**Need help?** Check the logs or use debug mode by setting `DEBUG=true` in your `.env` file.

