import 'package:flutter/material.dart';
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
    return SingleChildScrollView(
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
              const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.notifications_active, color: AssistIQTheme.primary),
                  SizedBox(width: 8),
                  Text(
                    'DISPATCH & ESCALATION ALERTS',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, letterSpacing: 0.8),
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
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          if (_isLoading)
            const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
          else if (_events.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(color: AssistIQTheme.surfaceContainerLow, borderRadius: BorderRadius.circular(6)),
              child: const Center(
                child: Text('No active escalations. All SLA timers healthy!', style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
              ),
            )
          else
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _events.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final ev = _events[index];
                final isAck = ev.acknowledgedAt != null;

                return Card(
                  color: isAck ? Colors.white : const Color(0xFFFFECEB),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
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
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: isAck ? AssistIQTheme.primary : AssistIQTheme.error,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      ev.triggerType,
                                      style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      '#${ev.caseRef ?? ''} — ${ev.caseTitle ?? ''}',
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            if (!isAck)
                              TextButton(
                                onPressed: () => _acknowledge(ev.id),
                                child: const Text('Acknowledge', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                              )
                            else
                              const Text('✓ Acknowledged', style: TextStyle(fontSize: 10, color: AssistIQTheme.primary, fontWeight: FontWeight.bold)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(ev.reason, style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 6),
                        Text(
                          'Target Role: ${ev.notifiedRole} | Created: ${ev.createdAt.length >= 16 ? ev.createdAt.substring(0, 16) : ev.createdAt}',
                          style: const TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }
}
