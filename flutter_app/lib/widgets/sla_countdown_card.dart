import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../core/theme.dart';
import '../models/case_model.dart';

class SLACountdownCard extends StatelessWidget {
  final SLAInfo? sla;
  final String priority;

  const SLACountdownCard({super.key, this.sla, required this.priority});

  @override
  Widget build(BuildContext context) {
    final isBreached = (sla?.responseBreached ?? false) || (sla?.resolveBreached ?? false);

    return Container(
      decoration: AssistIQTheme.liquidGlassDecoration(
        radius: 14,
        baseColor: isBreached ? const Color(0xFFFFF0EE).withValues(alpha: 0.95) : Colors.white.withValues(alpha: 0.9),
        border: Border.all(
          color: isBreached ? AssistIQTheme.error.withValues(alpha: 0.4) : const Color(0x3377786C),
        ),
      ),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.timer_outlined, size: 16, color: AssistIQTheme.primary),
                  const SizedBox(width: 6),
                  Text(
                    '24/7 SLA TRACKING',
                    style: GoogleFonts.outfit(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.6,
                      color: AssistIQTheme.primary,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                decoration: BoxDecoration(
                  color: isBreached ? AssistIQTheme.error : AssistIQTheme.primary,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  isBreached ? 'BREACHED' : 'HEALTHY',
                  style: GoogleFonts.jetBrainsMono(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'FIRST RESPONSE',
                      style: GoogleFonts.jetBrainsMono(fontSize: 9, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      sla?.firstResponseAt != null
                          ? '✓ Met Response'
                          : sla?.responseBreached ?? false
                              ? 'Response Breached'
                              : '${sla?.minutesToResponseDeadline ?? 0}m left',
                      style: GoogleFonts.inter(
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
                    Text(
                      'RESOLVE DEADLINE',
                      style: GoogleFonts.jetBrainsMono(fontSize: 9, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      sla?.resolvedAt != null
                          ? '✓ Case Resolved'
                          : sla?.resolveBreached ?? false
                              ? 'Resolve Breached'
                              : '${((sla?.minutesToResolveDeadline ?? 0) / 60).toStringAsFixed(1)}h left',
                      style: GoogleFonts.inter(
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
    );
  }
}
