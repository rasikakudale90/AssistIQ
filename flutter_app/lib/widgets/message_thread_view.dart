import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
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
            Row(
              children: [
                const Icon(Icons.forum_outlined, size: 16, color: AssistIQTheme.primary),
                const SizedBox(width: 6),
                Text(
                  'COMMUNICATION THREAD (${_messages.length})',
                  style: GoogleFonts.outfit(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.6, color: AssistIQTheme.onSurface),
                ),
              ],
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
            padding: const EdgeInsets.all(18),
            width: double.infinity,
            decoration: AssistIQTheme.liquidGlassDecoration(radius: 12),
            child: Center(
              child: Text(
                'No messages recorded yet.',
                style: GoogleFonts.inter(fontSize: 12, fontStyle: FontStyle.italic, color: AssistIQTheme.onSurfaceVariant),
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
                decoration: AssistIQTheme.liquidGlassDecoration(
                  radius: 12,
                  baseColor: isInternal ? const Color(0xFFFFF8E7).withValues(alpha: 0.95) : Colors.white.withValues(alpha: 0.9),
                  border: Border.all(
                    color: isInternal ? AssistIQTheme.tertiaryContainer.withValues(alpha: 0.4) : const Color(0x3377786C),
                  ),
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
                              style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface),
                            ),
                            const SizedBox(width: 6),
                            if (isInternal)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AssistIQTheme.tertiaryContainer,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'INTERNAL',
                                  style: GoogleFonts.jetBrainsMono(fontSize: 8, color: Colors.white, fontWeight: FontWeight.bold),
                                ),
                              ),
                            if (m.aiGenerated)
                              Container(
                                margin: const EdgeInsets.only(left: 4),
                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AssistIQTheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'AI DRAFT',
                                  style: GoogleFonts.jetBrainsMono(fontSize: 8, color: Colors.white, fontWeight: FontWeight.bold),
                                ),
                              ),
                          ],
                        ),
                        Text(
                          m.createdAt.length >= 16 ? m.createdAt.substring(11, 16) : '',
                          style: GoogleFonts.jetBrainsMono(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      m.body,
                      style: GoogleFonts.inter(fontSize: 12, height: 1.4, color: AssistIQTheme.onSurface),
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
              Text('Public Note', style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface)),
              const SizedBox(width: 12),
              Radio<String>(
                value: 'internal_only',
                groupValue: _visibility,
                onChanged: (val) => setState(() => _visibility = val!),
                activeColor: AssistIQTheme.tertiary,
              ),
              Text('Internal Only', style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.tertiary, fontWeight: FontWeight.bold)),
            ],
          ),

        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: TextField(
                controller: _msgController,
                maxLines: 3,
                style: GoogleFonts.inter(fontSize: 13, color: AssistIQTheme.onSurface),
                decoration: InputDecoration(
                  hintText: _visibility == 'internal_only'
                      ? 'Add internal investigation notes...'
                      : 'Write a response to the requester...',
                  hintStyle: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.outline),
                  filled: true,
                  fillColor: _visibility == 'internal_only' ? const Color(0xFFFFFBEF) : Colors.white.withValues(alpha: 0.9),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0x3377786C)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0x3377786C)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: AssistIQTheme.primary, width: 1.5),
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: _isSending ? null : _sendMessage,
              style: ElevatedButton.styleFrom(
                backgroundColor: AssistIQTheme.primary,
                foregroundColor: Colors.white,
                elevation: 2,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
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
