import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/app_theme.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _searchController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Search')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search for lost or found items...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.camera_alt),
                  onPressed: _searchByImage,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                _buildSearchOption(Icons.image, 'Image Search', () {}),
                const SizedBox(width: 16),
                _buildSearchOption(Icons.location_on, 'Nearby', () {}),
              ],
            ),
            const SizedBox(height: 32),
            const Text(
              'Recent Searches',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView(
                children: [
                  _buildRecentSearch('Blue laptop bag'),
                  _buildRecentSearch('Black wallet'),
                  _buildRecentSearch('iPhone 15'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchOption(IconData icon, String label, VoidCallback onTap) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFFE2E8F0)),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(icon, color: AppTheme.primaryColor),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentSearch(String text) {
    return ListTile(
      leading: const Icon(Icons.history, color: AppTheme.textSecondary),
      title: Text(text),
      trailing: const Icon(Icons.north_west, size: 16),
      onTap: () {},
    );
  }

  void _searchByImage() {
    // TODO: Implement image search
  }
}
