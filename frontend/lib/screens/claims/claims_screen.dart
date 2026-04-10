import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/app_theme.dart';

class ClaimsScreen extends ConsumerWidget {
  const ClaimsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Claims'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'My Claims'),
              Tab(text: 'Incoming'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildClaimsList('my'),
            _buildClaimsList('incoming'),
          ],
        ),
      ),
    );
  }

  Widget _buildClaimsList(String type) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 3,
      itemBuilder: (context, index) => Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
            child: const Icon(Icons.assignment, color: AppTheme.primaryColor),
          ),
          title: Text('Claim #${index + 1}'),
          subtitle: const Text('Pending review'),
          trailing: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.warningColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text('Pending', style: TextStyle(color: AppTheme.warningColor, fontSize: 12)),
          ),
        ),
      ),
    );
  }
}
