# AIMOR Frontend

React-based dashboard for the Smart Lost & Found System.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on http://localhost:8000

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

## 📁 Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   └── Layout.jsx           # Main layout with sidebar
│   ├── context/
│   │   └── AuthContext.jsx      # Authentication state
│   ├── pages/
│   │   ├── Login.jsx            # Login page
│   │   ├── Register.jsx          # Registration page
│   │   ├── Dashboard.jsx        # Main dashboard
│   │   ├── LostItems.jsx        # Lost items list
│   │   ├── FoundItems.jsx       # Found items list
│   │   ├── Search.jsx           # Search page
│   │   ├── Claims.jsx           # Claims management
│   │   ├── Notifications.jsx    # Notifications
│   │   ├── Profile.jsx          # User profile
│   │   ├── ItemDetail.jsx      # Item details
│   │   └── CreateItem.jsx       # Create item form
│   ├── services/
│   │   └── api.js               # API service layer
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## 🎨 Features

### Dashboard
- Overview statistics
- Recent items
- Quick actions

### Lost & Found Items
- View all items
- Filter by category/status
- Search functionality
- Create new items
- View item details

### Search
- Text-based search
- Image-based search
- Filter by category and type

### Claims Management
- View my claims
- View incoming claims
- Accept/Reject/Complete claims

### Notifications
- Real-time notifications
- Mark as read
- Clear notifications

### Profile
- Update personal info
- Change password

## 🔧 Configuration

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 📦 Dependencies

- **React 18** - UI framework
- **React Router 6** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## 🌐 API Integration

The frontend connects to the backend API. Make sure the backend is running:

```bash
# Backend (separate terminal)
cd backend
python -m app.main
```

## 🎯 Pages & Routes

| Route | Page | Description |
|-------|------|-------------|
| `/login` | Login | User login |
| `/register` | Register | User registration |
| `/dashboard` | Dashboard | Main dashboard |
| `/lost-items` | Lost Items | View lost items |
| `/lost-items/create` | Create Item | Report lost item |
| `/found-items` | Found Items | View found items |
| `/found-items/create` | Create Item | Report found item |
| `/search` | Search | Search by image/text |
| `/claims` | Claims | Manage claims |
| `/notifications` | Notifications | View notifications |
| `/profile` | Profile | User profile |

## 🔐 Authentication

- JWT-based authentication
- Token stored in localStorage
- Auto-redirect to login on 401

## 📱 Responsive Design

The dashboard is fully responsive:
- Mobile: Collapsible sidebar
- Tablet: Full sidebar
- Desktop: Full sidebar

## 🚀 Deployment

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 📝 Default Credentials

```
Email: admin@aimor.com
Password: admin123
```
