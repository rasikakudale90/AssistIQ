import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../models/case_model.dart';

class SLACountdownCard extends StatelessWidget {
  final SLAInfo? sla;
  final String priority;

  const SLACountdownCard({super.key, this.sla, required this.priority});

  @override
  Widget build(BuildContext context) {
    final isBreached = (sla?.responseBreached ?? false) || (sla?.resolveBreached ?? false);

    return Card(
      color: isBreached ? const Color(0xFFFFECEB) : AssistIQTheme.surfaceContainerLow,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.between,
              children: [
                const Row(
                  children: [
                    Icon(Icons.timer_outlined, size: 16, color: AssistIQTheme.primary),
                    SizedBox(width: 6),
                    Text(
                      '24/7 SLA TRACKING',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.8,
                        color: AssistIQTheme.primary,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: isBreached ? AssistIQTheme.error : AssistIQTheme.primary,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    isBreached ? 'BREACHED' : 'HEALTHY',
                    style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'FIRST RESPONSE',
                        style: TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        sla?.firstResponseAt != null
                            ? '✓ Met Response'
                            : sla?.responseBreached ?? false
                                ? 'Response Breached'
                                : '${sla?.minutesToResponseDeadline ?? 0}m left',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: (sla?.responseBreached ?? false) && sla?.firstResponseAt == null
                              ? AssistIQTheme.error
                              : AssistIQTheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'RESOLVE DEADLINE',
                        style: TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        sla?.resolvedAt != null
                            ? '✓ Case Resolved'
                            : sla?.resolveBreached ?? false
                                ? 'Resolve Breached'
                                : '${((sla?.minutesToResolveDeadline ?? 0) / 60).toStringAsFixed(1)}h left',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: (sla?.resolveBreached ?? false) && sla?.resolvedAt == null
                              ? AssistIQTheme.error
                              : AssistIQTheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
