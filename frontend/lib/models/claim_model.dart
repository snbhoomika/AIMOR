class Claim {
  final String id;
  final String lostItemId;
  final String foundItemId;
  final String claimantId;
  final String ownerId;
  final String message;
  final String status;
  final double? similarityScore;
  final String? responseMessage;
  final String? meetingLocation;
  final DateTime createdAt;

  Claim({
    required this.id,
    required this.lostItemId,
    required this.foundItemId,
    required this.claimantId,
    required this.ownerId,
    required this.message,
    required this.status,
    this.similarityScore,
    this.responseMessage,
    this.meetingLocation,
    required this.createdAt,
  });

  factory Claim.fromJson(Map<String, dynamic> json) {
    return Claim(
      id: json['id'],
      lostItemId: json['lost_item_id'],
      foundItemId: json['found_item_id'],
      claimantId: json['claimant_id'],
      ownerId: json['owner_id'],
      message: json['message'],
      status: json['status'],
      similarityScore: json['similarity_score']?.toDouble(),
      responseMessage: json['response_message'],
      meetingLocation: json['meeting_location'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
