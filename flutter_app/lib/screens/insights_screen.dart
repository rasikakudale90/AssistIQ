import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../providers/insights_provider.dart';

class InsightsScreen extends StatefulWidget {
  const InsightsScreen({super.key});

  @override
  State<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<InsightsProvider>(context, listen: false).fetchInsights();
    });
  }

  @override
  Widget build(BuildContext context) {
    final insProv = Provider.of<InsightsProvider>(context);
    final data = insProv.insights;

    return AmbientBackground(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Cycle Selector Pills
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
                      child: const Icon(Icons.analytics_outlined, color: AssistIQTheme.primary, size: 20),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'OPERATIONAL INSIGHTS',
                      style: GoogleFonts.outfit(fontSize: 13, fontWeight: FontWeight.bold, letterSpacing: 0.6, color: AssistIQTheme.onSurface),
                    ),
                  ],
                ),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: ['7d', '30d', '90d', 'all'].map((w) {
                      final isSel = insProv.timeWindow == w;
                      return Padding(
                        padding: const EdgeInsets.only(left: 4),
                        child: ChoiceChip(
                          label: Text(w.toUpperCase(), style: GoogleFonts.jetBrainsMono(fontSize: 10, fontWeight: FontWeight.bold, color: isSel ? Colors.white : AssistIQTheme.onSurfaceVariant)),
                          selected: isSel,
                          selectedColor: AssistIQTheme.primary,
                          backgroundColor: Colors.white.withValues(alpha: 0.6),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          onSelected: (_) => insProv.fetchInsights(w),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),

            if (insProv.isLoading)
              const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
            else if (data != null) ...[
              // AI Diagnostic Narrative Card
              Container(
                decoration: AssistIQTheme.liquidGlassDecoration(
                  radius: 16,
                  baseColor: Colors.white.withValues(alpha: 0.92),
                ),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.psychology, size: 18, color: AssistIQTheme.primary),
                            const SizedBox(width: 6),
                            Text(
                              'AI DIAGNOSTIC NARRATIVE',
                              style: GoogleFonts.outfit(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.primary, letterSpacing: 0.5),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                          decoration: BoxDecoration(
                            color: AssistIQTheme.primaryContainer,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text('HIGH CONFIDENCE', style: GoogleFonts.jetBrainsMono(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      data.aiNarrative ??
                          'During this ${data.timeWindow.toUpperCase()} reporting cycle, ${data.totalCases} dockets were logged with ${data.slaComplianceRatePercent}% overall SLA compliance.',
                      style: GoogleFonts.inter(fontSize: 13, height: 1.45, color: AssistIQTheme.onSurface),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AssistIQTheme.tertiaryContainer.withValues(alpha: 0.08),
                        border: Border.all(color: AssistIQTheme.tertiaryContainer.withValues(alpha: 0.25)),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.lightbulb_outline, size: 18, color: AssistIQTheme.tertiary),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('SYSTEM RECOMMENDATION', style: GoogleFonts.jetBrainsMono(fontSize: 9, fontWeight: FontWeight.bold, color: AssistIQTheme.tertiary, letterSpacing: 0.5)),
                                const SizedBox(height: 2),
                                Text('Focus operator bandwidth on initial response queues to maintain SLA targets above 95.0%.', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.onSurfaceVariant)),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              // 4 KPI Metric Cards
              GridView.count(
                crossAxisCount: MediaQuery.of(context).size.width > 600 ? 4 : 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 10,
                mainAxisSpacing: 10,
                childAspectRatio: 1.1,
                children: [
                  _buildKpiCard('TICKET VOLUME', '${data.totalCases}', 'Resolved: ${data.resolvedCases}', Icons.folder_open),
                  _buildKpiCard('24/7 SLA RATE', '${data.slaComplianceRatePercent}%', 'Target: 95.0%', Icons.timer_outlined, color: data.slaComplianceRatePercent >= 90 ? AssistIQTheme.primary : AssistIQTheme.error),
                  _buildKpiCard(
                    'AVG MTTR',
                    data.avgResolutionMinutes > 60
                        ? '${(data.avgResolutionMinutes / 60).toStringAsFixed(1)}h'
                        : '${data.avgResolutionMinutes.toInt()}m',
                    'Resolution Time',
                    Icons.speed,
                  ),
                  _buildKpiCard('REOPEN RATE', '${data.reopenRatePercent}%', 'Benchmark < 5%', Icons.refresh, color: AssistIQTheme.primary),
                ],
              ),
              const SizedBox(height: 14),

              // Support Team Metrics
              Container(
                decoration: AssistIQTheme.liquidGlassDecoration(
                  radius: 16,
                  baseColor: Colors.white.withValues(alpha: 0.92),
                ),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('SUPPORT TEAM BREAKDOWN', style: GoogleFonts.outfit(fontSize: 12, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface)),
                    const SizedBox(height: 10),
                    ...data.teamMetrics.map(
                      (tm) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 5),
                        child: Wrap(
                          alignment: WrapAlignment.spaceBetween,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          spacing: 8,
                          runSpacing: 4,
                          children: [
                            Text(tm.teamName, style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface)),
                            Text('Assigned: ${tm.assignedCount} | Resolved: ${tm.resolvedCount} | Breaches: ${tm.breachCount}', style: GoogleFonts.jetBrainsMono(fontSize: 11, color: AssistIQTheme.onSurfaceVariant)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildKpiCard(String title, String value, String sub, IconData icon, {Color? color}) {
    return Container(
      decoration: AssistIQTheme.liquidGlassDecoration(
        radius: 14,
        baseColor: Colors.white.withValues(alpha: 0.88),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.jetBrainsMono(fontSize: 9, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                ),
              ),
              Icon(icon, size: 14, color: AssistIQTheme.onSurfaceVariant),
            ],
          ),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: GoogleFonts.outfit(fontSize: 20, fontWeight: FontWeight.bold, color: color ?? AssistIQTheme.onSurface),
            ),
          ),
          Text(
            sub,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.inter(fontSize: 9, color: AssistIQTheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}
