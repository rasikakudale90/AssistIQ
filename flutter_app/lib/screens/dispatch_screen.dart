import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../core/api_client.dart';
import '../models/escalation_model.dart';
import '../providers/case_provider.dart';

class DispatchScreen extends StatefulWidget {
  const DispatchScreen({super.key});

  @override
  State<DispatchScreen> createState() => _DispatchScreenState();
}

class _DispatchScreenState extends State<DispatchScreen> {
  List<EscalationEventModel> _events = [];
  bool _isLoading = true;
  bool _isSweeping = false;

  @override
  void initState() {
    super.initState();
    _loadAlerts();
  }

  Future<void> _loadAlerts() async {
    setState(() => _isLoading = true);
    final caseProv = Provider.of<CaseProvider>(context, listen: false);
    final List<EscalationEventModel> allEvents = [];

    for (final c in caseProv.cases) {
      try {
        final res = await ApiClient.get('/cases/${c.id}/escalations');
        if (res is List) {
          for (final ev in res) {
            allEvents.add(EscalationEventModel.fromJson({
              ...ev,
              'case_ref': c.referenceNumber,
              'case_title': c.title,
            }));
          }
        }
      } catch (_) {}
    }

    allEvents.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    setState(() {
      _events = allEvents;
      _isLoading = false;
    });
  }

  Future<void> _triggerSweep() async {
    setState(() => _isSweeping = true);
    try {
      await ApiClient.post('/scheduler/sweep');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('The Sweep background scheduler evaluated all open cases!')),
        );
      }
      await _loadAlerts();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Sweep failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSweeping = false);
      }
    }
  }

  Future<void> _acknowledge(String id) async {
    try {
      await ApiClient.post('/escalations/$id/acknowledge');
      await _loadAlerts();
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return AmbientBackground(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 8,
              runSpacing: 8,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: AssistIQTheme.primaryContainer.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.notifications_active, color: AssistIQTheme.primary, size: 20),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'DISPATCH & ESCALATION ALERTS',
                      style: GoogleFonts.outfit(fontSize: 13, fontWeight: FontWeight.bold, letterSpacing: 0.6, color: AssistIQTheme.onSurface),
                    ),
                  ],
                ),
                ElevatedButton.icon(
                  onPressed: _isSweeping ? null : _triggerSweep,
                  icon: const Icon(Icons.bolt, size: 16),
                  label: Text(_isSweeping ? 'RUNNING...' : 'TRIGGER SWEEP'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AssistIQTheme.primary,
                    foregroundColor: Colors.white,
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    textStyle: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 11, letterSpacing: 0.5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),

            if (_isLoading)
              const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
            else if (_events.isEmpty)
              Container(
                padding: const EdgeInsets.all(28),
                decoration: AssistIQTheme.liquidGlassDecoration(radius: 16),
                child: Center(
                  child: Column(
                    children: [
                      const Icon(Icons.verified, size: 36, color: AssistIQTheme.primary),
                      const SizedBox(height: 10),
                      Text(
                        'All SLA Timers Healthy',
                        style: GoogleFonts.outfit(fontSize: 14, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'No pending dispatch escalations or breached thresholds.',
                        style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurfaceVariant),
                      ),
                    ],
                  ),
                ),
              )
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _events.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) {
                  final ev = _events[index];
                  final isAck = ev.acknowledgedAt != null;

                  return Container(
                    decoration: AssistIQTheme.liquidGlassDecoration(
                      radius: 14,
                      baseColor: isAck ? Colors.white.withValues(alpha: 0.88) : const Color(0xFFFFF0EE).withValues(alpha: 0.95),
                      border: Border.all(
                        color: isAck ? const Color(0x3377786C) : AssistIQTheme.error.withValues(alpha: 0.4),
                      ),
                    ),
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                                    decoration: BoxDecoration(
                                      color: isAck ? AssistIQTheme.primary : AssistIQTheme.error,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      ev.triggerType,
                                      style: GoogleFonts.jetBrainsMono(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      '#${ev.caseRef ?? ''} — ${ev.caseTitle ?? ''}',
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            if (!isAck)
                              TextButton(
                                onPressed: () => _acknowledge(ev.id),
                                style: TextButton.styleFrom(
                                  backgroundColor: AssistIQTheme.secondary.withValues(alpha: 0.12),
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                                ),
                                child: Text('Acknowledge', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.secondary)),
                              )
                            else
                              Text('✓ Acknowledged', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.primary, fontWeight: FontWeight.bold)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(ev.reason, style: GoogleFonts.inter(fontSize: 12, height: 1.4, color: AssistIQTheme.onSurface)),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.group_outlined, size: 14, color: AssistIQTheme.onSurfaceVariant),
                            const SizedBox(width: 4),
                            Text(
                              'Target: ${ev.notifiedRole} • ${ev.createdAt.length >= 16 ? ev.createdAt.substring(0, 16) : ev.createdAt}',
                              style: GoogleFonts.jetBrainsMono(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}
