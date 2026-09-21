import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../models/message_model.dart';
import '../providers/auth_provider.dart';
import '../providers/case_provider.dart';

class MessageThreadView extends StatefulWidget {
  final String caseId;

  const MessageThreadView({super.key, required this.caseId});

  @override
  State<MessageThreadView> createState() => _MessageThreadViewState();
}

class _MessageThreadViewState extends State<MessageThreadView> {
  final TextEditingController _msgController = TextEditingController();
  List<MessageModel> _messages = [];
  bool _isLoading = true;
  String _visibility = 'requester_visible';
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    _loadMessages();
  }

  Future<void> _loadMessages() async {
    setState(() => _isLoading = true);
    final caseProv = Provider.of<CaseProvider>(context, listen: false);
    final msgs = await caseProv.getMessages(widget.caseId);
    setState(() {
      _messages = msgs;
      _isLoading = false;
    });
  }

  Future<void> _sendMessage() async {
    if (_msgController.text.trim().isEmpty) return;
    setState(() => _isSending = true);

    try {
      final caseProv = Provider.of<CaseProvider>(context, listen: false);
      await caseProv.postMessage(widget.caseId, _msgController.text.trim(), _visibility);
      _msgController.clear();
      await _loadMessages();
    } finally {
      setState(() => _isSending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final isStaff = auth.user?.role != 'Requester';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'COMMUNICATION THREAD (${_messages.length})',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8),
            ),
            IconButton(
              icon: const Icon(Icons.refresh, size: 18),
              onPressed: _loadMessages,
              tooltip: 'Refresh Thread',
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Messages List
        if (_isLoading)
          const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()))
        else if (_messages.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            width: double.infinity,
            decoration: BoxDecoration(
              color: AssistIQTheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Center(
              child: Text(
                'No messages recorded yet.',
                style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: AssistIQTheme.onSurfaceVariant),
              ),
            ),
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _messages.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final m = _messages[index];
              final isInternal = m.visibility == 'internal_only';

              return Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isInternal ? const Color(0xFFFFF9E6) : Colors.white,
                  border: Border.all(
                    color: isInternal ? const Color(0xFFE6C663) : const Color(0x33C7C7B9),
                  ),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Text(
                              m.senderEmail ?? 'Operator',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(width: 6),
                            if (isInternal)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                decoration: BoxDecoration(
                                  color: AssistIQTheme.tertiaryContainer,
                                  borderRadius: BorderRadius.circular(3),
                                ),
                                child: const Text(
                                  'INTERNAL',
                                  style: TextStyle(fontSize: 9, color: Colors.white, fontWeight: FontWeight.bold),
                                ),
                              ),
                            if (m.aiGenerated)
                              Container(
                                margin: const EdgeInsets.only(left: 4),
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                decoration: BoxDecoration(
                                  color: AssistIQTheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(3),
                                ),
                                child: const Text(
                                  'AI DRAFT',
                                  style: TextStyle(fontSize: 9, color: Colors.white, fontWeight: FontWeight.bold),
                                ),
                              ),
                          ],
                        ),
                        Text(
                          m.createdAt.length >= 16 ? m.createdAt.substring(11, 16) : '',
                          style: const TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      m.body,
                      style: const TextStyle(fontSize: 13, height: 1.4),
                    ),
                  ],
                ),
              );
            },
          ),

        const SizedBox(height: 12),

        // Post Message Box
        if (isStaff)
          Row(
            children: [
              Radio<String>(
                value: 'requester_visible',
                groupValue: _visibility,
                onChanged: (val) => setState(() => _visibility = val!),
                activeColor: AssistIQTheme.primary,
              ),
              const Text('Public Note', style: TextStyle(fontSize: 12)),
              const SizedBox(width: 12),
              Radio<String>(
                value: 'internal_only',
                groupValue: _visibility,
                onChanged: (val) => setState(() => _visibility = val!),
                activeColor: AssistIQTheme.tertiary,
              ),
              const Text('Internal Only', style: TextStyle(fontSize: 12, color: AssistIQTheme.tertiary)),
            ],
          ),

        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: TextField(
                controller: _msgController,
                maxLines: 3,
                style: const TextStyle(fontSize: 13),
                decoration: InputDecoration(
                  hintText: _visibility == 'internal_only'
                      ? 'Add internal investigation notes...'
                      : 'Write a response to the requester...',
                  filled: true,
                  fillColor: _visibility == 'internal_only' ? const Color(0xFFFFFBEF) : Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: const BorderSide(color: AssistIQTheme.outlineVariant),
                  ),
                  contentPadding: const EdgeInsets.all(10),
                ),
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: _isSending ? null : _sendMessage,
              style: ElevatedButton.styleFrom(
                backgroundColor: AssistIQTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
              ),
              child: _isSending
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.send, size: 18),
            ),
          ],
        ),
      ],
    );
  }
}
