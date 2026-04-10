import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/app_theme.dart';

class ReportLostScreen extends ConsumerStatefulWidget {
  const ReportLostScreen({super.key});

  @override
  ConsumerState<ReportLostScreen> createState() => _ReportLostScreenState();
}

class _ReportLostScreenState extends ConsumerState<ReportLostScreen> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _locationController = TextEditingController();
  String _selectedCategory = 'bag';
  String _selectedColor = 'blue';

  final _categories = [
    'bag', 'wallet', 'phone', 'keys', 'bottle', 'laptop',
    'id_card', 'umbrella', 'watch', 'earphones', 'books', 'others'
  ];

  final _colors = [
    'black', 'white', 'blue', 'red', 'green', 'yellow',
    'orange', 'purple', 'pink', 'brown', 'gray', 'other'
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Report Lost Item')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image Upload
            GestureDetector(
              onTap: _pickImage,
              child: Container(
                height: 160,
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.primaryColor.withOpacity(0.3)),
                ),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.camera_alt, size: 48, color: AppTheme.primaryColor),
                      SizedBox(height: 8),
                      Text('Tap to add photos', style: TextStyle(color: AppTheme.textSecondary)),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            TextField(
              controller: _titleController,
              decoration: const InputDecoration(
                labelText: 'Item Title',
                hintText: 'e.g., Blue Laptop Bag',
              ),
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _descriptionController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Description',
                hintText: 'Describe the item in detail...',
              ),
            ),
            const SizedBox(height: 16),

            DropdownButtonFormField<String>(
              value: _selectedCategory,
              decoration: const InputDecoration(labelText: 'Category'),
              items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (value) => setState(() => _selectedCategory = value!),
            ),
            const SizedBox(height: 16),

            DropdownButtonFormField<String>(
              value: _selectedColor,
              decoration: const InputDecoration(labelText: 'Color'),
              items: _colors.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (value) => setState(() => _selectedColor = value!),
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _locationController,
              decoration: const InputDecoration(
                labelText: 'Last Seen Location',
                prefixIcon: Icon(Icons.location_on),
                hintText: 'Where did you lose it?',
              ),
            ),
            const SizedBox(height: 32),

            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _submit,
                child: const Text('Submit Report', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _pickImage() {
    // TODO: Implement image picker
  }

  void _submit() {
    // TODO: Implement submission
  }
}
