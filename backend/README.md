# AIMOR Backend API

<div align="center">

![AIMOR](https://img.shields.io/badge/AIMOR-Lost%20%26%20Found-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow)

**Smart Lost & Found System Using Deep Learning-Based Image and Text Matching**

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-endpoints) • [Database](#-database-schema)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Authentication](#-authentication)
- [Deployment](#-deployment)

---

## 🎯 Overview

AIMOR (AI-based Missing Object Recovery) is a full-stack Lost & Found system that uses deep learning for intelligent image and text matching. Users can report lost or found items, and the system automatically finds potential matches using ML-powered similarity search.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Image Matching** | Upload an image to find similar items using CNN feature extraction |
| **Text Search** | Search items using natural language descriptions |
| **Hybrid Matching** | Combines image and text similarity for accurate results |
| **Geolocation** | Find items near your location |
| **Real-time Notifications** | Get notified when matches are found |
| **Claim System** | Streamlined process to claim and return items |

---

## ✨ Features

### Authentication & Users
- User registration and login with JWT
- Profile management
- Role-based access (User, Admin, Moderator)
- Password change functionality

### Lost Items Management
- Report lost items with images and descriptions
- Add location, color, brand, and distinguishing features
- Track status (Active, Matched, Claimed, Returned)
- Auto-expire after 90 days

### Found Items Management
- Report found items with current holding location
- Admin verification system
- Similar tracking as lost items

### Search & Matching
- **Image-based search**: Upload image, get similar items
- **Text-based search**: Search by description
- **Nearby search**: Find items within radius
- **Auto-matching**: System suggests potential matches

### Claims Workflow
- Create claims linking lost and found items
- Verification questions for authenticity
- Accept/Reject/Complete workflow
- Meeting arrangement support

### Notifications
- Real-time notifications for matches and claims
- Unread count tracking
- Mark as read/delete functionality

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI 0.109.0 |
| **Database** | MongoDB 7.0 with Motor (async) |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt (passlib) |
| **Image Processing** | Pillow |
| **Validation** | Pydantic 2.0 |
| **ASGI Server** | Uvicorn |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic settings configuration
│   │   └── database.py            # MongoDB connection & indexes
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User schemas (create, update, response)
│   │   ├── item.py                # Lost/Found item schemas
│   │   ├── claim.py               # Claim schemas
│   │   └── notification.py        # Notification schemas
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                # /api/v1/auth/*
│   │   ├── lost_items.py          # /api/v1/lost-items/*
│   │   ├── found_items.py         # /api/v1/found-items/*
│   │   ├── search.py              # /api/v1/search/*
│   │   ├── claims.py              # /api/v1/claims/*
│   │   └── notifications.py       # /api/v1/notifications/*
│   │
│   └── utils/
│       ├── __init__.py
│       ├── security.py            # JWT, password hashing, auth deps
│       └── file_handler.py        # File upload, image processing
│
├── uploads/                       # Uploaded files directory
│   ├── lost-items/
│   ├── found-items/
│   ├── search/
│   └── avatars/
│
├── scripts/
│   └── init_db.py                 # Database initialization script
│
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- MongoDB 7.0+ (local or Atlas)
- pip (Python package manager)

### Installation

**1. Clone and navigate to backend:**
```bash
cd AIMOR/backend
```

**2. Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure environment:**
```bash
# Edit .env file with your settings
# Default configuration works for local MongoDB
```

**5. Initialize database:**
```bash
python scripts/init_db.py
```

**6. Start the server:**
```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

**7. Access the API:**
- **API Base URL**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@aimor.com | admin123 |

---

## 🔐 Environment Variables

Create a `.env` file in the backend root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=aimor_lost_found

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Configuration
APP_NAME=AIMOR Lost & Found System
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# File Upload Configuration
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "gif", "webp"]

# ML Configuration
ML_SERVICE_URL=http://localhost:8001
SIMILARITY_THRESHOLD=0.7
```

---

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api/v1`

All protected endpoints require `Authorization: Bearer <token>` header.

---

### 🔑 Authentication Endpoints

#### `POST /auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword123",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "65a1b2c3d4e5f6a7b8c9d0e1",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

---

#### `POST /auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):** Same as register response

---

#### `GET /auth/me` 🔒
Get current authenticated user's information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "65a1b2c3d4e5f6a7b8c9d0e1",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "avatar": null,
  "created_at": "2024-01-15T10:30:00"
}
```

---

#### `PUT /auth/me` 🔒
Update current user's profile.

**Request Body (all fields optional):**
```json
{
  "full_name": "John Smith",
  "phone": "+1987654321",
  "avatar": "/uploads/avatars/profile.jpg"
}
```

---

#### `POST /auth/change-password` 🔒
Change user's password.

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

---

#### `POST /auth/logout`
Logout (client should delete token).

---

### 📦 Lost Items Endpoints

#### `POST /lost-items/` 🔒
Report a new lost item.

**Request (multipart/form-data):**
```
title: "Blue Laptop Bag"
description: "Navy blue laptop bag with MacBook Pro inside, has a red keychain"
category: "bag"
date: "2024-01-15T14:30:00"
color: "blue"
brand: "Dell"
distinguishing_features: "Has a small tear on the left side"
location: "Library Building, 2nd Floor"
latitude: 37.7749
longitude: -122.4194
images: [file1.jpg, file2.jpg]
```

**Categories:**
- `bag`, `wallet`, `phone`, `keys`, `bottle`, `laptop`
- `id_card`, `umbrella`, `watch`, `earphones`, `books`, `others`

**Response (201 Created):**
```json
{
  "id": "65a1b2c3d4e5f6a7b8c9d0e2",
  "title": "Blue Laptop Bag",
  "description": "Navy blue laptop bag with MacBook Pro inside...",
  "category": "bag",
  "date": "2024-01-15T14:30:00",
  "color": "blue",
  "brand": "Dell",
  "distinguishing_features": "Has a small tear on the left side",
  "location": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749],
    "address": "Library Building, 2nd Floor"
  },
  "images": ["/uploads/lost-items/abc123.jpg"],
  "user_id": "65a1b2c3d4e5f6a7b8c9d0e1",
  "status": "active",
  "views": 0,
  "match_count": 0,
  "created_at": "2024-01-15T15:00:00"
}
```

---

#### `GET /lost-items/` 🔒
Get all lost items with pagination and filters.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | - | Filter by category |
| `status` | string | - | Filter by status (active, matched, returned) |
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page (max 100) |

**Response (200 OK):** Array of lost items

---

#### `GET /lost-items/my` 🔒
Get current user's lost items.

---

#### `GET /lost-items/{item_id}` 🔒
Get a specific lost item by ID. Increments view count.

---

#### `PUT /lost-items/{item_id}` 🔒
Update a lost item (owner only).

**Request (multipart/form-data):** Any field can be updated

---

#### `DELETE /lost-items/{item_id}` 🔒
Delete a lost item (owner only).

---

#### `POST /lost-items/{item_id}/mark-returned` 🔒
Mark item as returned.

---

### 🔍 Found Items Endpoints

#### `POST /found-items/` 🔒
Report a found item.

**Request (multipart/form-data):**
```
title: "Black Wallet"
description: "Black leather wallet found near the cafeteria"
category: "wallet"
date: "2024-01-15T12:00:00"
color: "black"
brand: "Tommy Hilfiger"
current_location: "Security Office, Main Building"
location: "Cafeteria"
latitude: 37.7749
longitude: -122.4194
images: [wallet1.jpg]
```

---

#### `GET /found-items/` 🔒
Get all found items.

**Additional Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `verified_only` | boolean | false | Show only verified items |

---

#### `GET /found-items/my` 🔒
Get current user's found items.

---

#### `GET /found-items/{item_id}` 🔒
Get specific found item.

---

#### `PUT /found-items/{item_id}` 🔒
Update found item (owner only).

---

#### `DELETE /found-items/{item_id}` 🔒
Delete found item (owner only).

---

#### `POST /found-items/{item_id}/verify` 🔒 (Admin)
Verify a found item (admin only).

---

### 🔎 Search & Matching Endpoints

#### `POST /search/image` 🔒
Search for items by uploading an image.

**Request (multipart/form-data):**
```
image: [search_image.jpg]
category: bag (optional)
limit: 10
item_type: found (found/lost/all)
```

**Response (200 OK):**
```json
{
  "search_image": "/uploads/search/xyz789.jpg",
  "total_matches": 5,
  "matches": [
    {
      "id": "65a1b2c3d4e5f6a7b8c9d0e2",
      "title": "Blue Backpack",
      "description": "Similar blue backpack...",
      "category": "bag",
      "images": ["/uploads/found-items/abc123.jpg"],
      "similarity_score": 0.92,
      "match_type": "image"
    }
  ]
}
```

---

#### `POST /search/text` 🔒
Search items by text description.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query_text` | string | required | Search text (min 3 chars) |
| `category` | string | - | Filter by category |
| `color` | string | - | Filter by color |
| `limit` | integer | 20 | Results limit |
| `item_type` | string | found | Search in (found/lost/all) |

---

#### `GET /search/nearby` 🔒
Search for items near a location.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude` | float | required | User latitude |
| `longitude` | float | required | User longitude |
| `radius` | float | 1000 | Search radius in meters |
| `category` | string | - | Filter by category |
| `limit` | integer | 20 | Results limit |

---

#### `GET /search/matches/{item_id}` 🔒
Get potential matches for a specific item.

**Response (200 OK):**
```json
{
  "item_id": "65a1b2c3d4e5f6a7b8c9d0e2",
  "item_type": "lost",
  "total_matches": 8,
  "matches": [
    {
      "id": "65a1b2c3d4e5f6a7b8c9d0e3",
      "title": "Black Backpack",
      "description": "Found black backpack...",
      "category": "bag",
      "images": ["/uploads/found-items/def456.jpg"],
      "similarity_score": 0.85,
      "match_type": "auto"
    }
  ]
}
```

---

#### `GET /search/categories`
Get all available item categories.

**Response (200 OK):**
```json
{
  "categories": [
    {"value": "bag", "label": "Bag"},
    {"value": "wallet", "label": "Wallet"},
    {"value": "phone", "label": "Phone"},
    {"value": "keys", "label": "Keys"},
    {"value": "bottle", "label": "Bottle"},
    {"value": "laptop", "label": "Laptop"},
    {"value": "id_card", "label": "ID Card"},
    {"value": "umbrella", "label": "Umbrella"},
    {"value": "watch", "label": "Watch"},
    {"value": "earphones", "label": "Earphones"},
    {"value": "books", "label": "Books"},
    {"value": "others", "label": "Others"}
  ]
}
```

---

### 📝 Claims Endpoints

#### `POST /claims/` 🔒
Create a new claim for a lost item.

**Request Body:**
```json
{
  "lost_item_id": "65a1b2c3d4e5f6a7b8c9d0e2",
  "found_item_id": "65a1b2c3d4e5f6a7b8c9d0e3",
  "message": "This looks like my backpack! I can describe the contents inside.",
  "verification_questions": [
    {
      "question": "What color is the laptop inside?",
      "answer": "Space Gray MacBook Pro"
    },
    {
      "question": "What's in the front pocket?",
      "answer": "A red notebook and pens"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "65a1b2c3d4e5f6a7b8c9d0e4",
  "lost_item_id": "65a1b2c3d4e5f6a7b8c9d0e2",
  "found_item_id": "65a1b2c3d4e5f6a7b8c9d0e3",
  "message": "This looks like my backpack!",
  "claimant_id": "65a1b2c3d4e5f6a7b8c9d0e1",
  "owner_id": "65a1b2c3d4e5f6a7b8c9d0e5",
  "status": "pending",
  "created_at": "2024-01-15T16:00:00"
}
```

---

#### `GET /claims/my-claims` 🔒
Get claims made by current user.

**Query Parameters:** `status` (pending/accepted/rejected/completed)

---

#### `GET /claims/incoming` 🔒
Get claims made to your found items.

---

#### `GET /claims/{claim_id}` 🔒
Get specific claim details.

---

#### `PUT /claims/{claim_id}/accept` 🔒
Accept a claim (found item owner only).

**Request Body (optional):**
```json
{
  "response_message": "Yes, this is correct! Let's meet.",
  "meeting_location": "Library entrance, 2 PM tomorrow"
}
```

---

#### `PUT /claims/{claim_id}/reject` 🔒
Reject a claim.

**Request Body (optional):**
```json
{
  "response_message": "The description doesn't match the item."
}
```

---

#### `PUT /claims/{claim_id}/complete` 🔒
Mark claim as completed (item returned).

---

### 🔔 Notifications Endpoints

#### `GET /notifications/` 🔒
Get user's notifications.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `unread_only` | boolean | false | Show only unread |
| `limit` | integer | 50 | Max results |

**Response (200 OK):**
```json
[
  {
    "id": "65a1b2c3d4e5f6a7b8c9d0e6",
    "user_id": "65a1b2c3d4e5f6a7b8c9d0e1",
    "type": "match_found",
    "title": "Potential Match Found!",
    "message": "A similar item to your lost bag was found.",
    "data": {
      "lost_item_id": "65a1b2c3d4e5f6a7b8c9d0e2",
      "found_item_id": "65a1b2c3d4e5f6a7b8c9d0e3"
    },
    "read": false,
    "created_at": "2024-01-15T16:30:00"
  }
]
```

**Notification Types:**
- `match_found` - Similar item found
- `claim_received` - Someone claimed your found item
- `claim_accepted` - Your claim was accepted
- `claim_rejected` - Your claim was rejected
- `item_returned` - Item successfully returned
- `system` - System notifications

---

#### `GET /notifications/unread-count` 🔒
Get count of unread notifications.

**Response:**
```json
{
  "unread_count": 5
}
```

---

#### `PUT /notifications/{notification_id}/read` 🔒
Mark a notification as read.

---

#### `PUT /notifications/read-all` 🔒
Mark all notifications as read.

---

#### `DELETE /notifications/{notification_id}` 🔒
Delete a notification.

---

#### `DELETE /notifications/clear-all` 🔒
Clear all notifications.

---

## 🗄️ Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  full_name: String,
  hashed_password: String,
  phone: String (optional),
  role: String ("user" | "admin" | "moderator"),
  avatar: String (optional),
  is_active: Boolean,
  is_verified: Boolean,
  last_login: Date,
  created_at: Date,
  updated_at: Date
}
```

### Lost Items Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  title: String,
  description: String,
  category: String,
  date: Date,
  color: String (optional),
  brand: String (optional),
  distinguishing_features: String (optional),
  location: {
    type: "Point",
    coordinates: [Number, Number],
    address: String
  },
  images: [String],
  image_embeddings: [Number] (optional),
  status: String ("active" | "matched" | "claimed" | "returned" | "expired"),
  views: Number,
  match_count: Number,
  created_at: Date,
  updated_at: Date,
  expires_at: Date
}
```

### Found Items Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  title: String,
  description: String,
  category: String,
  date: Date,
  color: String (optional),
  brand: String (optional),
  distinguishing_features: String (optional),
  location: {
    type: "Point",
    coordinates: [Number, Number],
    address: String
  },
  current_location: String (optional),
  images: [String],
  image_embeddings: [Number] (optional),
  status: String,
  is_verified: Boolean,
  views: Number,
  match_count: Number,
  created_at: Date,
  updated_at: Date
}
```

### Claims Collection
```javascript
{
  _id: ObjectId,
  lost_item_id: String,
  found_item_id: String,
  claimant_id: String,
  owner_id: String,
  message: String,
  verification_questions: [{
    question: String,
    answer: String
  }],
  status: String ("pending" | "accepted" | "rejected" | "completed" | "cancelled"),
  similarity_score: Number,
  response_message: String,
  meeting_location: String,
  meeting_date: Date,
  created_at: Date,
  updated_at: Date
}
```

### Notifications Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  type: String,
  title: String,
  message: String,
  data: Object (optional),
  read: Boolean,
  created_at: Date
}
```

---

## 🔐 Authentication

### JWT Token Structure

The API uses JWT Bearer tokens for authentication.

**Token Payload:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1705312800
}
```

**Token Lifetime:** 24 hours (configurable)

### Using Protected Endpoints

Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
     http://localhost:8000/api/v1/auth/me
```

---

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t aimor-backend .
docker run -p 8000:8000 aimor-backend
```

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Set `DEBUG=False`
- [ ] Configure MongoDB replica set
- [ ] Set up HTTPS with reverse proxy (nginx)
- [ ] Configure CORS for specific origins
- [ ] Set up proper backup for MongoDB
- [ ] Configure log aggregation

---

## 🤝 Integration with ML Service

The backend is designed to integrate with your ML model. To connect:

1. **Update the ML Service URL** in `.env`:
   ```env
   ML_SERVICE_URL=http://localhost:8001
   ```

2. **Modify `search.py`** to call your ML service:
   ```python
   import httpx
   
   async def extract_features(image_path: str):
       async with httpx.AsyncClient() as client:
           response = await client.post(
               f"{settings.ML_SERVICE_URL}/extract",
               files={"image": open(image_path, "rb")}
           )
           return response.json()["embedding"]
   ```

3. **Update matching logic** to use real cosine similarity with embeddings.

---

## 📞 Support

For issues or questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Open an issue on GitHub

---

## 📄 License

MIT License - See LICENSE file for details.
