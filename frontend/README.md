# AIMOR Frontend (Flutter)

<div align="center">

![Flutter](https://img.shields.io/badge/Flutter-3.5.3-blue)
![Dart](https://img.shields.io/badge/Dart-3.5.3-blue)
![Riverpod](https://img.shields.io/badge/Riverpod-2.4.9-green)

**Mobile Frontend for AIMOR - AI-based Missing Object Recovery System**

</div>

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Flutter 3.5.3 |
| **Language** | Dart |
| **State Management** | Riverpod |
| **Navigation** | GoRouter |
| **Networking** | Dio |
| **Local Storage** | Flutter Secure Storage, Shared Preferences, Hive |
| **Image Handling** | Image Picker, Cached Network Image |
| **Location** | Geolocator, Google Maps Flutter |
| **UI Components** | Flutter ScreenUtil, Shimmer, Lottie, FL Chart |

---

## Project Structure

```
frontend/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── config/
│   │   ├── app_config.dart          # API URLs, keys, constants
│   │   ├── app_theme.dart           # Light/Dark theme configuration
│   │   └── app_router.dart          # GoRouter navigation setup
│   │
│   ├── models/
│   │   ├── user_model.dart          # User data model
│   │   ├── item_model.dart          # Lost/Found item model
│   │   ├── claim_model.dart         # Claim data model
│   │   └── notification_model.dart  # Notification data model
│   │
│   ├── services/
│   │   └── api_service.dart         # Dio API client (all endpoints)
│   │
│   ├── providers/
│   │   ├── auth_provider.dart       # Authentication state
│   │   └── items_provider.dart      # Items state management
│   │
│   ├── screens/
│   │   ├── splash_screen.dart       # App splash screen
│   │   ├── auth/
│   │   │   ├── login_screen.dart    # Login page
│   │   │   └── register_screen.dart # Registration page
│   │   ├── home/
│   │   │   └── home_screen.dart     # Main shell with bottom nav
│   │   ├── items/
│   │   │   ├── lost_items_screen.dart    # Browse lost items
│   │   │   ├── found_items_screen.dart   # Browse found items
│   │   │   ├── report_lost_screen.dart   # Report lost item form
│   │   │   ├── report_found_screen.dart  # Report found item form
│   │   │   └── item_detail_screen.dart   # Item detail view
│   │   ├── search/
│   │   │   ├── search_screen.dart        # Search page
│   │   │   └── search_result_screen.dart # Search results
│   │   ├── claims/
│   │   │   └── claims_screen.dart       # Claims management
│   │   ├── profile/
│   │   │   └── profile_screen.dart      # User profile
│   │   └── notifications/
│   │       └── notifications_screen.dart # Notifications list
│   │
│   └── widgets/                     # Reusable UI components
│
├── assets/
│   ├── images/                      # Image assets
│   ├── icons/                       # Icon assets
│   └── animations/                  # Lottie animations
│
├── android/                         # Android platform files
├── ios/                             # iOS platform files
├── pubspec.yaml                     # Dependencies
└── README.md                        # This file
```

---

## Quick Start

### Prerequisites

- Flutter SDK 3.5.3+
- Android Studio / Xcode
- Running AIMOR Backend (see `../backend/README.md`)

### Installation

**1. Navigate to frontend:**
```bash
cd AIMOR/frontend
```

**2. Install dependencies:**
```bash
flutter pub get
```

**3. Run the app:**
```bash
# Android
flutter run

# iOS
flutter run -d ios

# List available devices
flutter devices
```

---

## Configuration

### API Base URL

Update `lib/config/app_config.dart`:

```dart
// For Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// For iOS Simulator
static const String baseUrl = 'http://localhost:8000';

// For Physical Device (replace with your IP)
static const String baseUrl = 'http://192.168.1.100:8000';
```

---

## Screens Overview

| Screen | Route | Description |
|--------|-------|-------------|
| Splash | `/splash` | App loading screen |
| Login | `/login` | User login |
| Register | `/register` | New user registration |
| Home | `/home` | Main dashboard |
| Lost Items | `/lost-items` | Browse lost items |
| Found Items | `/found-items` | Browse found items |
| Search | `/search` | Text/Image/Nearby search |
| Claims | `/claims` | Manage claims |
| Profile | `/profile` | User profile & settings |
| Report Lost | `/report-lost` | Report a lost item |
| Report Found | `/report-found` | Report a found item |
| Item Detail | `/item/:id` | View item details |
| Notifications | `/notifications` | View notifications |

---

## Key Features

- **Image Search**: Upload photos to find matching items using ML
- **Text Search**: Search by description
- **Nearby Search**: Find items near your location
- **Claim System**: Claim and return items with verification
- **Real-time Notifications**: Get notified of matches and claims
- **Offline Support**: Hive-based local storage for offline access

---

## Build Commands

```bash
# Debug build
flutter build apk --debug

# Release build
flutter build apk --release

# iOS build
flutter build ios --release
```

---

## Dependencies

See `pubspec.yaml` for full list. Key packages:

- `flutter_riverpod` - State management
- `dio` - HTTP client
- `go_router` - Declarative routing
- `image_picker` - Camera/gallery access
- `geolocator` - Location services
- `cached_network_image` - Image caching
- `flutter_secure_storage` - Secure token storage
- `fl_chart` - Charts and graphs

---

For backend API documentation, see [../backend/README.md](../backend/README.md)
