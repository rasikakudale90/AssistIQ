import 'package:flutter/material.dart';
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

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Cycle Selector Pills
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'OPERATIONAL INSIGHTS',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 0.8),
              ),
              Row(
                children: ['7d', '30d', '90d', 'all'].map((w) {
                  final isSel = insProv.timeWindow == w;
                  return Padding(
                    padding: const EdgeInsets.only(left: 4),
                    child: ChoiceChip(
                      label: Text(w.toUpperCase(), style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isSel ? Colors.white : null)),
                      selected: isSel,
                      selectedColor: AssistIQTheme.primary,
                      onSelected: (_) => insProv.fetchInsights(w),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
          const SizedBox(height: 12),

          if (insProv.isLoading)
            const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
          else if (data != null) ...[
            // AI Diagnostic Narrative Card
            Card(
              color: AssistIQTheme.surfaceContainerLow,
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.psychology, size: 18, color: AssistIQTheme.primary),
                            SizedBox(width: 6),
                            Text(
                              'AI DIAGNOSTIC NARRATIVE',
                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.primary),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: AssistIQTheme.primaryContainer, borderRadius: BorderRadius.circular(4)),
                          child: const Text('HIGH CONFIDENCE', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      data.aiNarrative ??
                          'During this ${data.timeWindow.toUpperCase()} reporting cycle, ${data.totalCases} dockets were logged with ${data.slaComplianceRatePercent}% overall SLA compliance.',
                      style: const TextStyle(fontSize: 13, height: 1.4),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),

            // 4 KPI Metric Cards
            GridView.count(
              crossAxisCount: MediaQuery.of(context).size.width > 600 ? 4 : 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 8,
              mainAxisSpacing: 8,
              childAspectRatio: 1.4,
              children: [
                _buildKpiCard('TICKET VOLUME', '${data.totalCases}', 'Resolved: ${data.resolvedCases}', Icons.folder_open),
                _buildKpiCard('24/7 SLA RATE', '${data.slaComplianceRatePercent}%', 'Target: 95.0%', Icons.timer_outlined, color: data.slaComplianceRatePercent >= 90 ? AssistIQTheme.primary : AssistIQTheme.error),
                _buildKpiCard('AVG MTTR', '${data.avgResolutionMinutes > 60 ? (data.avgResolutionMinutes / 60).toStringAsFixed(1) + 'h' : data.avgResolutionMinutes.toInt().toString() + 'm'}', 'Resolution Time', Icons.speed),
                _buildKpiCard('REOPEN RATE', '${data.reopenRatePercent}%', 'Benchmark < 5%', Icons.refresh, color: AssistIQTheme.primary),
              ],
            ),
            const SizedBox(height: 16),

            // Support Team Metrics
            Card(
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('SUPPORT TEAM BREAKDOWN', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 10),
                    ...data.teamMetrics.map(
                      (tm) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.between,
                          children: [
                            Text(tm.teamName, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                            Text('Assigned: ${tm.assignedCount} | Resolved: ${tm.resolvedCount} | Breaches: ${tm.breachCount}', style: const TextStyle(fontSize: 11, color: AssistIQTheme.onSurfaceVariant)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildKpiCard(String title, String value, String sub, IconData icon, {Color? color}) {
    return Card(
      color: AssistIQTheme.surfaceContainerLow,
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.between,
              children: [
                Text(title, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant)),
                Icon(icon, size: 14, color: AssistIQTheme.onSurfaceVariant),
              ],
            ),
            Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color ?? AssistIQTheme.onSurface)),
            Text(sub, style: const TextStyle(fontSize: 9, color: AssistIQTheme.onSurfaceVariant)),
          ],
        ),
      ),
    );
  }
}
