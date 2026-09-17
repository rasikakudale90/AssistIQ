class AttachmentModel {
  final String id;
  final String fileName;
  final int fileSize;
  final String mimeType;

  AttachmentModel({
    required this.id,
    required this.fileName,
    required this.fileSize,
    required this.mimeType,
  });

  factory AttachmentModel.fromJson(Map<String, dynamic> json) {
    return AttachmentModel(
      id: json['id'] as String,
      fileName: json['file_name'] as String,
      fileSize: json['file_size'] as int? ?? 0,
      mimeType: json['mime_type'] as String? ?? 'application/octet-stream',
    );
  }
}

class MessageModel {
  final String id;
  final String caseId;
  final String senderId;
  final String? senderEmail;
  final String visibility;
  final String body;
  final bool aiGenerated;
  final String createdAt;
  final List<AttachmentModel> attachments;

  MessageModel({
    required this.id,
    required this.caseId,
    required this.senderId,
    this.senderEmail,
    required this.visibility,
    required this.body,
    required this.aiGenerated,
    required this.createdAt,
    this.attachments = const [],
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    var rawAtts = json['attachments'] as List<dynamic>? ?? [];
    return MessageModel(
      id: json['id'] as String,
      caseId: json['case_id'] as String,
      senderId: json['sender_id'] as String,
      senderEmail: json['sender_email'] as String?,
      visibility: json['visibility'] as String? ?? 'requester_visible',
      body: json['body'] as String,
      aiGenerated: json['ai_generated'] as bool? ?? false,
      createdAt: json['created_at'] as String,
      attachments: rawAtts.map((a) => AttachmentModel.fromJson(a)).toList(),
    );
  }
}
