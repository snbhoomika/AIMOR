class Item {
  final String id;
  final String userId;
  final String title;
  final String description;
  final String category;
  final DateTime date;
  final String? color;
  final String? brand;
  final String? distinguishingFeatures;
  final ItemLocation location;
  final List<String> images;
  final String status;
  final int views;
  final int matchCount;
  final DateTime createdAt;
  final String itemType;

  Item({
    required this.id,
    required this.userId,
    required this.title,
    required this.description,
    required this.category,
    required this.date,
    this.color,
    this.brand,
    this.distinguishingFeatures,
    required this.location,
    required this.images,
    required this.status,
    required this.views,
    required this.matchCount,
    required this.createdAt,
    required this.itemType,
  });

  factory Item.fromJson(Map<String, dynamic> json, {String itemType = 'lost'}) {
    return Item(
      id: json['id'],
      userId: json['user_id'],
      title: json['title'],
      description: json['description'],
      category: json['category'],
      date: DateTime.parse(json['date']),
      color: json['color'],
      brand: json['brand'],
      distinguishingFeatures: json['distinguishing_features'],
      location: ItemLocation.fromJson(json['location'] ?? {}),
      images: List<String>.from(json['images'] ?? []),
      status: json['status'] ?? 'active',
      views: json['views'] ?? 0,
      matchCount: json['match_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at']),
      itemType: itemType,
    );
  }
}

class ItemLocation {
  final double latitude;
  final double longitude;
  final String? address;

  ItemLocation({
    required this.latitude,
    required this.longitude,
    this.address,
  });

  factory ItemLocation.fromJson(Map<String, dynamic> json) {
    final coords = json['coordinates'];
    return ItemLocation(
      latitude: coords != null ? (coords[1] as num).toDouble() : 0.0,
      longitude: coords != null ? (coords[0] as num).toDouble() : 0.0,
      address: json['address'],
    );
  }
}
