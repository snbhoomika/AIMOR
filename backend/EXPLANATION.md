# 📚 AIMOR Backend - Beginner's Guide

> **Note:** This project uses **FastAPI** (not Django). Both are Python web frameworks, but FastAPI is newer, faster, and easier to learn!

---

## 🎯 Table of Contents

1. [Big Picture Overview](#1-big-picture-overview)
2. [How a Request Flows](#2-how-a-request-flows)
3. [Database Connection Explained](#3-database-connection-explained)
4. [Models/Schemas Explained](#4-modelsschemas-explained)
5. [Routes/Endpoints Explained](#5-routesendpoints-explained)
6. [Authentication Explained](#6-authentication-explained)
7. [Complete Example Walkthrough](#7-complete-example-walkthrough)

---

## 1. Big Picture Overview

Think of the backend like a **restaurant**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🍽️ THE RESTAURANT ANALOGY                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   👤 CUSTOMER          👨‍🍳 KITCHEN           🗄️ PANTRY                    │
│   (Frontend/App)       (Backend/FastAPI)     (Database/MongoDB)            │
│                                                                             │
│   "I want a burger"  →  Receives order   →   Checks ingredients            │
│                       →  Prepares food   →   Stores food                   │
│                       →  Returns food    ←   Updates inventory             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The 3 Main Parts:

| Part | What It Does | In Our Code |
|------|--------------|-------------|
| **Frontend** | What user sees (buttons, forms) | React/Flutter app |
| **Backend** | Processes requests, business logic | FastAPI (`app/` folder) |
| **Database** | Stores data permanently | MongoDB |

---

## 2. How a Request Flows

When a user taps "Report Lost Item" on the app:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    📱 USER REPORTS A LOST BAG                               │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: USER ACTION
    User fills form: "Blue bag", "Library", uploads photo
         │
         ▼
Step 2: FRONTEND SENDS REQUEST
    POST http://localhost:8000/api/v1/lost-items/
    Body: { title: "Blue bag", description: "Library", image: ... }
         │
         ▼
Step 3: FASTAPI RECEIVES REQUEST
    ┌─────────────────────────────────────────────────────────┐
    │  app/main.py                                            │
    │  └── Routes to: app/routes/lost_items.py               │
    └─────────────────────────────────────────────────────────┘
         │
         ▼
Step 4: AUTHENTICATION CHECK
    ┌─────────────────────────────────────────────────────────┐
    │  Is user logged in? (Check JWT token)                   │
    │  → If NO: Return error 401                              │
    │  → If YES: Continue                                    │
    └─────────────────────────────────────────────────────────┘
         │
         ▼
Step 5: VALIDATE DATA
    ┌─────────────────────────────────────────────────────────┐
    │  Is title at least 3 characters?                        │
    │  Is image a valid JPG/PNG?                              │
    │  → If INVALID: Return error 400                         │
    │  → If VALID: Continue                                  │
    └─────────────────────────────────────────────────────────┘
         │
         ▼
Step 6: SAVE TO DATABASE
    ┌─────────────────────────────────────────────────────────┐
    │  app/core/database.py                                   │
    │  db.lost_items.insert_one(item_data)                   │
    └─────────────────────────────────────────────────────────┘
         │
         ▼
Step 7: RETURN RESPONSE
    Status: 201 Created
    Body: { id: "abc123", title: "Blue bag", ... }
         │
         ▼
Step 8: FRONTEND DISPLAYS RESULT
    "Item reported successfully!"
```

---

## 3. Database Connection Explained

### What is MongoDB?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MongoDB = Digital Filing Cabinet                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Traditional SQL Database          MongoDB (NoSQL)                         │
│   ─────────────────────────         ────────────────                        │
│   Database                          Database                                │
│   └── Table (rows & columns)        └── Collection (folders)                │
│       └── Row                           └── Document (JSON file)            │
│                                                                             │
│   Like Excel spreadsheet            Like folder of JSON files               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Our Collections (Folders):

```
aimor_lost_found (Database)
│
├── 📁 users/
│   ├── { _id: "1", email: "john@test.com", name: "John", ... }
│   ├── { _id: "2", email: "jane@test.com", name: "Jane", ... }
│   └── { _id: "3", email: "bob@test.com", name: "Bob", ... }
│
├── 📁 lost_items/
│   ├── { _id: "101", title: "Blue bag", user_id: "1", ... }
│   ├── { _id: "102", title: "Phone", user_id: "2", ... }
│   └── { _id: "103", title: "Keys", user_id: "1", ... }
│
├── 📁 found_items/
│   ├── { _id: "201", title: "Black wallet", user_id: "3", ... }
│   └── { _id: "202", title: "Umbrella", user_id: "3", ... }
│
├── 📁 claims/
│   └── { _id: "301", lost_item_id: "101", found_item_id: "201", ... }
│
└── 📁 notifications/
    └── { _id: "401", user_id: "1", type: "match_found", ... }
```

### How Connection Works:

**File: `app/core/database.py`**

```python
# Step 1: Import Motor (async MongoDB driver)
from motor.motor_asyncio import AsyncIOMotorClient

# Step 2: Create a database class to hold connection
class Database:
    client: AsyncIOMotorClient = None  # Connection to MongoDB
    db = None  # The specific database

database = Database()

# Step 3: Function to connect (called when app starts)
async def connect_to_mongo():
    # Create connection to MongoDB server
    database.client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    # Select our database
    database.db = database.client["aimor_lost_found"]
    
    print("Connected to MongoDB!")

# Step 4: Function to disconnect (called when app stops)
async def close_mongo_connection():
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")

# Step 5: Function to get database (used in routes)
def get_database():
    return database.db
```

### Visual Flow:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FastAPI    │     │    Motor     │     │   MongoDB    │
│   (App)      │────▶│   (Driver)   │────▶│  (Server)    │
│              │     │              │     │              │
│  Routes use  │     │  Translates  │     │  Stores data │
│  db object   │     │  Python to   │     │              │
│              │     │  MongoDB     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 4. Models/Schemas Explained

### What are Models?

Models are **blueprints** that define what data looks like.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    📋 MODEL = Form Template                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Think of a model like a registration form:                                │
│                                                                             │
│   ┌─────────────────────────────────┐                                       │
│   │  LOST ITEM FORM                 │                                       │
│   ├─────────────────────────────────┤                                       │
│   │  Title: [____________] (text)   │  ← Defines: title must be text       │
│   │  Description: [_________]       │  ← Defines: description is required  │
│   │  Category: [v Bag     ]         │  ← Defines: only specific values     │
│   │  Color: [____________] (opt)    │  ← Defines: color is optional        │
│   │  Images: [Upload...]            │  ← Defines: list of images           │
│   └─────────────────────────────────┘                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Our Models:

**File: `app/models/item.py`**

```python
# This defines what a Lost Item looks like
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Define allowed categories (like a dropdown list)
class ItemCategory(str, Enum):
    BAG = "bag"
    WALLET = "wallet"
    PHONE = "phone"
    KEYS = "keys"
    BOTTLE = "bottle"
    LAPTOP = "laptop"
    # ... more categories

# Schema for CREATING a new lost item
class LostItemCreate(BaseModel):
    title: str                    # Required text
    description: str              # Required text
    category: ItemCategory        # Must be one of the categories
    date: datetime                # When item was lost
    color: Optional[str] = None   # Optional text
    brand: Optional[str] = None   # Optional text
    # Note: user_id comes from authentication, not form

# Schema for RESPONDING (what we send back to user)
class LostItemResponse(BaseModel):
    id: str                       # MongoDB generates this
    title: str
    description: str
    category: ItemCategory
    date: datetime
    color: Optional[str]
    brand: Optional[str]
    images: List[str]             # URLs to uploaded images
    user_id: str                  # Who reported it
    status: str                   # active, matched, returned
    views: int                    # How many people viewed
    created_at: datetime          # When item was created
```

### Why Different Schemas?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DIFFERENT SCHEMAS FOR DIFFERENT PURPOSES                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   LostItemCreate         LostItemInDB              LostItemResponse         │
│   (User sends this)      (Stored in DB)            (Sent back to user)      │
│   ─────────────────      ───────────────           ───────────────────      │
│   • title                • _id (DB adds)           • id (formatted)         │
│   • description          • title                   • title                  │
│   • category             • description             • description            │
│   • date                 • category                • category               │
│   • color?               • date                    • date                   │
│   • brand?               • color?                  • color?                 │
│                          • brand?                  • brand?                 │
│                          • user_id                 • images                 │
│                          • status                  • user_id                │
│                          • created_at              • status                 │
│                          • image_embeddings?       • views                  │
│                                                    • created_at             │
│                                                                             │
│   Why? User doesn't need to see internal fields like image_embeddings      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Routes/Endpoints Explained

### What are Routes?

Routes are **URL handlers** - they decide what happens when someone visits a URL.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🛣️ ROUTES = Post Office Mail Sorting                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   URL Request                    Route Handler                               │
│   ───────────                    ─────────────                               │
│   POST /api/v1/auth/login    →   app/routes/auth.py → login()              │
│   GET  /api/v1/lost-items    →   app/routes/lost_items.py → get_items()    │
│   POST /api/v1/lost-items    →   app/routes/lost_items.py → create_item()  │
│                                                                             │
│   Like mail sorting:                                                        │
│   - Address determines destination                                          │
│   - Method (GET/POST) determines action                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Route Anatomy:

**File: `app/routes/lost_items.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from app.utils.security import get_current_user  # Authentication
from app.core.database import get_database        # Database access

# Create a router (like a group of related routes)
router = APIRouter(prefix="/lost-items", tags=["Lost Items"])

# -------------------------------------------------------
# POST /api/v1/lost-items/ - Create new lost item
# -------------------------------------------------------
@router.post("/", response_model=LostItemResponse)
async def create_lost_item(
    # Form data from user
    title: str = Form(...),
    description: str = Form(...),
    category: ItemCategory = Form(...),
    images: List[UploadFile] = File([]),
    
    # Current user (from JWT token) - automatically injected
    current_user: dict = Depends(get_current_user),
):
    """
    This function runs when someone POSTs to /lost-items/
    """
    
    # Step 1: Get database connection
    db = get_database()
    
    # Step 2: Upload images
    image_urls = await save_multiple_files(images)
    
    # Step 3: Create item document
    item_data = {
        "title": title,
        "description": description,
        "category": category,
        "user_id": str(current_user["_id"]),  # From logged-in user
        "images": image_urls,
        "status": "active",
        "created_at": datetime.utcnow(),
    }
    
    # Step 4: Save to database
    result = await db.lost_items.insert_one(item_data)
    
    # Step 5: Return response
    return LostItemResponse(
        id=str(result.inserted_id),
        title=title,
        description=description,
        # ... other fields
    )
```

### HTTP Methods:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HTTP METHODS = Actions you can do                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Method      URL                          Action     Like...               │
│   ──────      ───                          ──────     ────────               │
│   POST        /api/v1/lost-items/          Create     Adding new item       │
│   GET         /api/v1/lost-items/          Read       Viewing all items     │
│   GET         /api/v1/lost-items/123       Read       Viewing one item      │
│   PUT         /api/v1/lost-items/123       Update     Editing an item       │
│   DELETE      /api/v1/lost-items/123       Delete     Removing an item      │
│                                                                             │
│   CRUD = Create, Read, Update, Delete                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Authentication Explained

### How JWT Authentication Works:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🔐 JWT AUTHENTICATION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   STEP 1: LOGIN                                                             │
│   ┌──────────┐                         ┌──────────┐                         │
│   │ Frontend │ ─── POST /login ──────▶ │ Backend  │                         │
│   │          │   {email, password}     │          │                         │
│   └──────────┘                         └──────────┘                         │
│                                                   │                         │
│                                                   ▼                         │
│                                          Check database                     │
│                                          Verify password                    │
│                                                   │                         │
│                                                   ▼                         │
│   ┌──────────┐ ◀── Return token ────── ┌──────────┐                         │
│   │ Frontend │   {access_token: "eyJ.."}│ Backend  │                         │
│   └──────────┘                         └──────────┘                         │
│                                                                             │
│   STEP 2: STORE TOKEN                                                       │
│   Frontend stores token in browser localStorage                            │
│                                                                             │
│   STEP 3: AUTHENTICATED REQUEST                                             │
│   ┌──────────┐                         ┌──────────┐                         │
│   │ Frontend │ ─── GET /my-items ────▶ │ Backend  │                         │
│   │          │   Header:               │          │                         │
│   │          │   Authorization:        │          │                         │
│   │          │   Bearer eyJ..          │          │                         │
│   └──────────┘                         └──────────┘                         │
│                                                   │                         │
│                                                   ▼                         │
│                                          Verify token                       │
│                                          Get user from token                │
│                                                   │                         │
│                                                   ▼                         │
│   ┌──────────┐ ◀── Return data ────── ┌──────────┐                         │
│   │ Frontend │   (only user's items)  │ Backend  │                         │
│   └──────────┘                         └──────────┘                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Token Structure:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    JWT TOKEN = Encoded ID Card                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NWE4...          │
│          ──────────────────────────────────────────────────────────────     │
│                           │                              │                  │
│                           ▼                              ▼                  │
│                    HEADER (who signed)           PAYLOAD (user info)        │
│                                                                             │
│   Payload decoded:                                                          │
│   {                                                                         │
│     "sub": "65a8b2c3d4e5f6a7b8c9d0e1",  ← User ID                          │
│     "email": "john@test.com",            ← User email                      │
│     "exp": 1705312800                    ← Expiration time                  │
│   }                                                                         │
│                                                                             │
│   ⚠️ Token is NOT encrypted, just encoded. Don't put secrets in payload!   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Authentication Code:

**File: `app/utils/security.py`**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing (one-way, can't decrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if password matches hash"""
    # "password123" → "$2b$12$..." (hashed)
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Convert password to hash (for storage)"""
    # "password123" → "$2b$12$LJ3m4ys..."
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create a JWT token"""
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(security)):
    """Dependency that extracts user from token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        # Get user from database
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Using in Routes:

```python
# Protected route - requires login
@router.get("/my-items")
async def get_my_items(current_user: dict = Depends(get_current_user)):
    # current_user is automatically injected from JWT token!
    # If no valid token, this route won't even run (401 error)
    
    user_id = current_user["_id"]
    items = await db.lost_items.find({"user_id": user_id})
    return items
```

---

## 7. Complete Example Walkthrough

### Scenario: User Reports a Lost Bag

Let's trace the entire flow from start to finish:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    📱 COMPLETE FLOW: Report Lost Bag                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Step 1: User fills form on mobile app**
```
Title: "Blue Backpack"
Description: "Navy blue backpack with laptop inside"
Category: Bag
Color: Blue
Images: [backpack1.jpg, backpack2.jpg]
```

**Step 2: Frontend sends request**
```javascript
// Frontend code (React/Flutter)
fetch('http://localhost:8000/api/v1/lost-items/', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...',  // User's token
    },
    body: formData  // Contains title, description, images
})
```

**Step 3: FastAPI receives request**

```
Request arrives at FastAPI server:
┌─────────────────────────────────────────────────────────────────────────────┐
│ POST /api/v1/lost-items/                                                    │
│ Authorization: Bearer eyJhbGciOiJIUzI1NiIs...                               │
│                                                                             │
│ Form Data:                                                                  │
│   title: "Blue Backpack"                                                    │
│   description: "Navy blue backpack with laptop inside"                      │
│   category: "bag"                                                           │
│   color: "blue"                                                             │
│   images: [binary data]                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Step 4: Router matches URL**

```
FastAPI looks at routes:
├── /api/v1/auth/*          → auth.router
├── /api/v1/lost-items/*    → lost_items.router  ✓ MATCH!
├── /api/v1/found-items/*   → found_items.router
└── ...

Calls: lost_items.py → create_lost_item()
```

**Step 5: Authentication check**

```python
# This runs automatically before the function
current_user: dict = Depends(get_current_user)

# get_current_user() does:
# 1. Extract token from "Bearer eyJ..."
# 2. Decode token → {sub: "user123", email: "john@test.com"}
# 3. Find user in database: db.users.find_one({"_id": "user123"})
# 4. Return user object

# If token invalid → 401 error returned, function never runs
# If token valid → current_user = {_id: "user123", email: "john@test.com", ...}
```

**Step 6: Upload images**

```python
images: List[UploadFile] = File([])

# For each image:
# 1. Validate file type (jpg, png, etc.)
# 2. Generate unique filename: abc123.jpg
# 3. Resize if needed
# 4. Save to: ./uploads/lost-items/abc123.jpg
# 5. Return URL: /uploads/lost-items/abc123.jpg
```

**Step 7: Create document**

```python
item_data = {
    "title": "Blue Backpack",
    "description": "Navy blue backpack with laptop inside",
    "category": "bag",
    "color": "blue",
    "user_id": "user123",  # From current_user
    "images": ["/uploads/lost-items/abc123.jpg", "/uploads/lost-items/def456.jpg"],
    "status": "active",
    "views": 0,
    "match_count": 0,
    "created_at": datetime(2024, 1, 15, 10, 30, 0),
}
```

**Step 8: Save to database**

```python
result = await db.lost_items.insert_one(item_data)

# MongoDB receives:
# db.lost_items.insertOne({
#   title: "Blue Backpack",
#   description: "Navy blue...",
#   ...
# })

# MongoDB returns:
# { acknowledged: true, insertedId: ObjectId("65a8b2c3d4e5f6a7b8c9d0e2") }
```

**Step 9: Return response**

```python
return LostItemResponse(
    id="65a8b2c3d4e5f6a7b8c9d0e2",
    title="Blue Backpack",
    description="Navy blue backpack with laptop inside",
    category="bag",
    # ... all other fields
)

# Response sent:
# {
#   "id": "65a8b2c3d4e5f6a7b8c9d0e2",
#   "title": "Blue Backpack",
#   "description": "Navy blue backpack with laptop inside",
#   "category": "bag",
#   "color": "blue",
#   "images": ["/uploads/lost-items/abc123.jpg"],
#   "user_id": "user123",
#   "status": "active",
#   "views": 0,
#   "match_count": 0,
#   "created_at": "2024-01-15T10:30:00"
# }
```

**Step 10: Frontend displays result**

```javascript
// Frontend receives response
if (response.ok) {
    showMessage("Item reported successfully!");
    navigateTo("/my-items");
}
```

---

## 🗂️ File Summary - What Each File Does

```
backend/
│
├── app/
│   │
│   ├── main.py                    # 🚀 ENTRY POINT - Starts the server
│   │                              #   - Creates FastAPI app
│   │                              #   - Adds middleware (CORS, etc.)
│   │                              #   - Includes all routes
│   │                              #   - Starts/stops database connection
│   │
│   ├── core/
│   │   ├── config.py              # ⚙️ CONFIGURATION - App settings
│   │   │                          #   - MongoDB URL
│   │   │                          #   - Secret keys
│   │   │                          #   - File upload limits
│   │   │
│   │   └── database.py            # 🗄️ DATABASE - MongoDB connection
│   │                              #   - Connect to MongoDB
│   │                              #   - Create indexes
│   │                              #   - Provide db access to routes
│   │
│   ├── models/
│   │   ├── user.py                # 👤 USER SCHEMA - User data structure
│   │   │                          #   - What fields user has
│   │   │                          #   - Validation rules
│   │   │
│   │   ├── item.py                # 📦 ITEM SCHEMA - Lost/Found items
│   │   │                          #   - Item fields & types
│   │   │                          #   - Categories enum
│   │   │
│   │   ├── claim.py               # 📝 CLAIM SCHEMA - Claim data
│   │   │                          #   - Claim fields
│   │   │                          #   - Status enum
│   │   │
│   │   └── notification.py        # 🔔 NOTIFICATION SCHEMA
│   │
│   ├── routes/
│   │   ├── auth.py                # 🔐 AUTH ROUTES - Login/Register
│   │   │                          #   POST /auth/register
│   │   │                          #   POST /auth/login
│   │   │                          #   GET  /auth/me
│   │   │
│   │   ├── lost_items.py          # 📤 LOST ITEMS ROUTES
│   │   │                          #   POST   /lost-items/        (create)
│   │   │                          #   GET    /lost-items/        (list all)
│   │   │                          #   GET    /lost-items/{id}    (get one)
│   │   │                          #   PUT    /lost-items/{id}    (update)
│   │   │                          #   DELETE /lost-items/{id}    (delete)
│   │   │
│   │   ├── found_items.py         # 📥 FOUND ITEMS ROUTES (same pattern)
│   │   │
│   │   ├── search.py              # 🔎 SEARCH ROUTES - ML matching
│   │   │                          #   POST /search/image
│   │   │                          #   POST /search/text
│   │   │                          #   GET  /search/nearby
│   │   │
│   │   ├── claims.py              # ✋ CLAIMS ROUTES - Item claims
│   │   │                          #   POST /claims/
│   │   │                          #   PUT  /claims/{id}/accept
│   │   │
│   │   └── notifications.py       # 🔔 NOTIFICATION ROUTES
│   │
│   └── utils/
│       ├── security.py            # 🔑 SECURITY - Auth helpers
│       │                          #   - Create JWT tokens
│       │                          #   - Verify passwords
│       │                          #   - Get current user
│       │
│       └── file_handler.py        # 📁 FILE UPLOAD - Handle images
│                                  #   - Save uploaded files
│                                  #   - Validate file types
│                                  #   - Resize images
│
├── uploads/                       # 📂 STORAGE - Uploaded files
│   ├── lost-items/
│   ├── found-items/
│   └── avatars/
│
├── scripts/
│   └── init_db.py                 # 🔄 INIT SCRIPT - Setup database
│
├── .env                           # 🔧 ENVIRONMENT - Secret config
├── requirements.txt               # 📦 DEPENDENCIES - Python packages
└── README.md                      # 📖 DOCUMENTATION
```

---

## 🧠 Key Concepts Summary

| Concept | What It Is | Example |
|---------|------------|---------|
| **Endpoint/Route** | URL that handles requests | `/api/v1/lost-items/` |
| **HTTP Method** | Action to perform | GET, POST, PUT, DELETE |
| **Request Body** | Data sent to server | `{title: "Blue bag", ...}` |
| **Response** | Data sent back | `{id: "123", title: "Blue bag", ...}` |
| **Authentication** | Proving who you are | JWT token in header |
| **Middleware** | Code that runs before/after requests | CORS, logging |
| **Schema/Model** | Data structure definition | Pydantic models |
| **Async/Await** | Non-blocking operations | `await db.find()` |
| **Dependency Injection** | Auto-providing required objects | `Depends(get_current_user)` |

---

## 🚀 Next Steps

1. **Run the server**: `python -m app.main`
2. **Open Swagger UI**: http://localhost:8000/docs
3. **Test endpoints** directly in the browser
4. **Connect your frontend** to the API

Happy coding! 🎉
