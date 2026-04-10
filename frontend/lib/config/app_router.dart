import 'package:go_router/go_router.dart';
import '../screens/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/items/lost_items_screen.dart';
import '../screens/items/found_items_screen.dart';
import '../screens/items/report_lost_screen.dart';
import '../screens/items/report_found_screen.dart';
import '../screens/items/item_detail_screen.dart';
import '../screens/search/search_screen.dart';
import '../screens/search/search_result_screen.dart';
import '../screens/claims/claims_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/notifications/notifications_screen.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => HomeScreen(child: child),
        routes: [
          GoRoute(
            path: '/home',
            builder: (context, state) => const LostItemsScreen(),
          ),
          GoRoute(
            path: '/lost-items',
            builder: (context, state) => const LostItemsScreen(),
          ),
          GoRoute(
            path: '/found-items',
            builder: (context, state) => const FoundItemsScreen(),
          ),
          GoRoute(
            path: '/search',
            builder: (context, state) => const SearchScreen(),
          ),
          GoRoute(
            path: '/claims',
            builder: (context, state) => const ClaimsScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/report-lost',
        builder: (context, state) => const ReportLostScreen(),
      ),
      GoRoute(
        path: '/report-found',
        builder: (context, state) => const ReportFoundScreen(),
      ),
      GoRoute(
        path: '/item/:id',
        builder: (context, state) => ItemDetailScreen(
          itemId: state.pathParameters['id']!,
        ),
      ),
      GoRoute(
        path: '/search-results',
        builder: (context, state) => const SearchResultScreen(),
      ),
      GoRoute(
        path: '/notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),
    ],
  );
}
