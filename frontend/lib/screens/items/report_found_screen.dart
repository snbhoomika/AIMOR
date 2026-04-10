import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/app_theme.dart';

class ReportFoundScreen extends ConsumerStatefulWidget {
  const ReportFoundScreen({super.key});

  @override
  ConsumerState<ReportFoundScreen> createState() => _ReportFoundScreenState();
}

class _ReportFoundScreenState extends ConsumerState<ReportFoundScreen> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _locationController = TextEditingController();
  final _currentLocationController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Report Found Item')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            GestureDetector(
              onTap: () {},
              child: Container(
                height: 160,
                decoration: BoxDecoration(
                  color: AppTheme.successColor.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(16),
                  border:
                      Border.all(color: AppTheme.successColor.withOpacity(0.3)),
                ),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.camera_alt,
                          size: 48, color: AppTheme.successColor),
                      SizedBox(height: 8),
                      Text('Tap to add photos',
                          style: TextStyle(color: AppTheme.textSecondary)),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Item Title'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Description'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _currentLocationController,
              decoration: const InputDecoration(
                labelText: 'Current Holding Location',
                hintText: 'e.g., Security Office, Main Building',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _locationController,
              decoration: const InputDecoration(
                labelText: 'Found Location',
                prefixIcon: Icon(Icons.location_on),
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () {},
                child:
                    const Text('Submit Report', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
