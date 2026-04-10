import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/app_theme.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          TextButton(
            onPressed: () {},
            child: const Text('Mark all read'),
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 5,
        itemBuilder: (context, index) => _buildNotificationCard(index),
      ),
    );
  }

  Widget _buildNotificationCard(int index) {
    final icons = [
      Icons.search,
      Icons.assignment,
      Icons.check_circle,
      Icons.info,
      Icons.emoji_events
    ];
    final colors = [
      AppTheme.primaryColor,
      AppTheme.warningColor,
      AppTheme.successColor,
      AppTheme.textSecondary,
      AppTheme.accentColor
    ];

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: colors[index].withOpacity(0.1),
          child: Icon(icons[index], color: colors[index]),
        ),
        title: Text('Notification #${index + 1}'),
        subtitle: const Text('A match was found for your item'),
        trailing: index < 2
            ? Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: AppTheme.primaryColor,
                  shape: BoxShape.circle,
                ),
              )
            : null,
        onTap: () {},
      ),
    );
  }
}
