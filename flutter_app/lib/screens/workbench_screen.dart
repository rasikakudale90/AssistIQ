import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../models/case_model.dart';
import '../providers/case_provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/app_header.dart';
import '../widgets/sla_countdown_card.dart';
import '../widgets/message_thread_view.dart';
import 'case_intake_sheet.dart';
import 'insights_screen.dart';
import 'dispatch_screen.dart';
import 'knowledge_screen.dart';
import 'admin_screen.dart';

class WorkbenchScreen extends StatefulWidget {
  const WorkbenchScreen({super.key});

  @override
  State<WorkbenchScreen> createState() => _WorkbenchScreenState();
}

class _WorkbenchScreenState extends State<WorkbenchScreen> {
  int _currentNavIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<CaseProvider>(context, listen: false).fetchCases();
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final isStaff = auth.user?.role != 'Requester';

    final navDestinations = [
      const NavigationDestination(icon: Icon(Icons.table_rows_outlined), selectedIcon: Icon(Icons.table_rows), label: 'Workbench'),
      if (isStaff) const NavigationDestination(icon: Icon(Icons.query_stats_outlined), selectedIcon: Icon(Icons.query_stats), label: 'Insights'),
      if (isStaff) const NavigationDestination(icon: Icon(Icons.notifications_active_outlined), selectedIcon: Icon(Icons.notifications_active), label: 'Dispatch'),
      const NavigationDestination(icon: Icon(Icons.menu_book_outlined), selectedIcon: Icon(Icons.menu_book), label: 'Knowledge'),
      if (isStaff) const NavigationDestination(icon: Icon(Icons.admin_panel_settings_outlined), selectedIcon: Icon(Icons.admin_panel_settings), label: 'Admin'),
    ];

    return Scaffold(
      appBar: const AppHeader(title: 'Operations Console'),
      body: AmbientBackground(
        child: _buildCurrentTab(context),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.9),
          border: const Border(top: BorderSide(color: Color(0x3377786C))),
        ),
        child: NavigationBar(
          backgroundColor: Colors.transparent,
          indicatorColor: AssistIQTheme.primary.withValues(alpha: 0.15),
          selectedIndex: _currentNavIndex,
          onDestinationSelected: (idx) => setState(() => _currentNavIndex = idx),
          destinations: navDestinations,
        ),
      ),
      floatingActionButton: _currentNavIndex == 0
          ? FloatingActionButton.extended(
              onPressed: () {
                showModalBottomSheet(
                  context: context,
                  isScrollControlled: true,
                  backgroundColor: Colors.transparent,
                  builder: (_) => const CaseIntakeSheet(),
                );
              },
              icon: const Icon(Icons.add_circle, color: Colors.white, size: 20),
              label: Text('NEW INTAKE', style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold, letterSpacing: 0.5)),
              backgroundColor: AssistIQTheme.primary,
              elevation: 4,
            )
          : null,
    );
  }

  Widget _buildCurrentTab(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final isStaff = auth.user?.role != 'Requester';

    if (_currentNavIndex == 0) {
      return _buildWorkbenchView(context);
    } else if (isStaff && _currentNavIndex == 1) {
      return const InsightsScreen();
    } else if (isStaff && _currentNavIndex == 2) {
      return const DispatchScreen();
    } else if ((isStaff && _currentNavIndex == 3) || (!isStaff && _currentNavIndex == 1)) {
      return const KnowledgeScreen();
    } else {
      return const AdminScreen();
    }
  }

  Widget _buildWorkbenchView(BuildContext context) {
    final caseProv = Provider.of<CaseProvider>(context);
    final selected = caseProv.selectedCase;
    final isWide = MediaQuery.of(context).size.width > 800;

    return LayoutBuilder(
      builder: (context, constraints) {
        if (isWide) {
          // Split Master-Detail Layout
          return Row(
            children: [
              SizedBox(
                width: 380,
                child: _buildQueueList(context),
              ),
              const VerticalDivider(width: 1, color: Color(0x3377786C)),
              Expanded(
                child: selected != null
                    ? _buildDetailPane(context, selected)
                    : Center(
                        child: Text(
                          'Select a docket from the queue to view details',
                          style: GoogleFonts.inter(color: AssistIQTheme.outline),
                        ),
                      ),
              ),
            ],
          );
        } else {
          // Single Column Mobile Layout
          return _buildQueueList(context);
        }
      },
    );
  }

  Widget _buildQueueList(BuildContext context) {
    final caseProv = Provider.of<CaseProvider>(context);
    final filtered = caseProv.filteredCases;

    return Column(
      children: [
        // Filter Pills
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: ['ALL', 'ACTIVE', 'BREACHED', 'UNASSIGNED'].map((f) {
                final isSel = caseProv.filter == f;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(
                      f,
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: isSel ? Colors.white : AssistIQTheme.onSurfaceVariant,
                      ),
                    ),
                    selected: isSel,
                    selectedColor: AssistIQTheme.primary,
                    backgroundColor: Colors.white.withValues(alpha: 0.8),
                    side: BorderSide(color: isSel ? AssistIQTheme.primary : const Color(0x3377786C)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    onSelected: (_) => caseProv.setFilter(f),
                  ),
                );
              }).toList(),
            ),
          ),
        ),

        // Case Cards List
        Expanded(
          child: caseProv.isLoading
              ? const Center(child: CircularProgressIndicator(color: AssistIQTheme.primary))
              : filtered.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.inbox_outlined, size: 40, color: AssistIQTheme.outline.withValues(alpha: 0.6)),
                          const SizedBox(height: 8),
                          Text(
                            'No cases matching filter',
                            style: GoogleFonts.inter(fontSize: 13, color: AssistIQTheme.outline),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      itemCount: filtered.length,
                      itemBuilder: (context, index) {
                        final c = filtered[index];
                        final isSel = caseProv.selectedCase?.id == c.id;

                        Color priorityColor = AssistIQTheme.primary;
                        if (c.priority == 'P1') priorityColor = AssistIQTheme.error;
                        if (c.priority == 'P2') priorityColor = AssistIQTheme.secondary;
                        if (c.priority == 'P4') priorityColor = AssistIQTheme.tertiary;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          decoration: AssistIQTheme.liquidGlassDecoration(
                            radius: 14,
                            baseColor: isSel
                                ? AssistIQTheme.primaryContainer.withValues(alpha: 0.15)
                                : Colors.white.withValues(alpha: 0.85),
                            border: isSel
                                ? Border.all(color: AssistIQTheme.primary, width: 1.5)
                                : Border.all(color: const Color(0x2E77786C)),
                          ),
                          child: Material(
                            color: Colors.transparent,
                            child: InkWell(
                              borderRadius: BorderRadius.circular(14),
                              onTap: () {
                                caseProv.selectCase(c);
                                if (MediaQuery.of(context).size.width <= 800) {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (_) => Scaffold(
                                        appBar: AppHeader(title: '#${c.referenceNumber}'),
                                        body: AmbientBackground(
                                          child: SingleChildScrollView(child: _buildDetailPane(context, c)),
                                        ),
                                      ),
                                    ),
                                  );
                                }
                              },
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Row(
                                          children: [
                                            Text(
                                              '#${c.referenceNumber}',
                                              style: GoogleFonts.jetBrainsMono(
                                                fontSize: 12,
                                                fontWeight: FontWeight.bold,
                                                color: AssistIQTheme.primary,
                                              ),
                                            ),
                                            const SizedBox(width: 8),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: priorityColor.withValues(alpha: 0.15),
                                                borderRadius: BorderRadius.circular(6),
                                                border: Border.all(color: priorityColor.withValues(alpha: 0.4)),
                                              ),
                                              child: Text(
                                                c.priority,
                                                style: GoogleFonts.jetBrainsMono(
                                                  fontSize: 10,
                                                  color: priorityColor,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                          decoration: BoxDecoration(
                                            color: AssistIQTheme.surfaceContainerHigh,
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text(
                                            c.status,
                                            style: GoogleFonts.inter(
                                              fontSize: 10,
                                              fontWeight: FontWeight.w600,
                                              color: AssistIQTheme.onSurface,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      c.title,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: GoogleFonts.inter(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: AssistIQTheme.onSurface,
                                      ),
                                    ),
                                    if (c.description.isNotEmpty) ...[
                                      const SizedBox(height: 2),
                                      Text(
                                        c.description,
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: GoogleFonts.inter(
                                          fontSize: 11,
                                          color: AssistIQTheme.onSurfaceVariant,
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ),
                          ),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  Widget _buildDetailPane(BuildContext context, CaseModel c) {
    final caseProv = Provider.of<CaseProvider>(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: AssistIQTheme.liquidGlassElevatedDecoration(radius: 18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    '#${c.referenceNumber} — ${c.title}',
                    style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AssistIQTheme.primary,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    c.status,
                    style: GoogleFonts.inter(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              c.description,
              style: GoogleFonts.inter(fontSize: 13, height: 1.5, color: AssistIQTheme.onSurface),
            ),
            const SizedBox(height: 16),

            // SLA Card
            SLACountdownCard(sla: c.sla, priority: c.priority),
            const SizedBox(height: 16),

            // Status Transition Quick Buttons
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (c.status == 'New')
                  ElevatedButton(
                    onPressed: () => caseProv.updateStatus(c.id, 'InAssessment', c.version),
                    child: const Text('Start Assessment'),
                  ),
                if (c.status == 'InAssessment')
                  ElevatedButton(
                    onPressed: () => caseProv.updateStatus(c.id, 'Assigned', c.version),
                    child: const Text('Assign Case'),
                  ),
                if (c.status == 'Assigned')
                  ElevatedButton(
                    onPressed: () => caseProv.updateStatus(c.id, 'Resolved', c.version),
                    child: const Text('Mark Resolved'),
                  ),
                if (c.status == 'Resolved') ...[
                  ElevatedButton(
                    onPressed: () => caseProv.updateStatus(c.id, 'Closed', c.version),
                    child: const Text('Confirm Fix & Close'),
                  ),
                  OutlinedButton(
                    onPressed: () => caseProv.updateStatus(c.id, 'Assigned', c.version),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AssistIQTheme.secondary,
                      side: const BorderSide(color: AssistIQTheme.secondary),
                    ),
                    child: const Text('Reject Fix (Still Broken)'),
                  ),
                ],
                if (c.status == 'Closed')
                  ElevatedButton.icon(
                    onPressed: () => _showReopenDialog(context, caseProv, c.id),
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text('Reopen (7-Day Window)'),
                    style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.secondary, foregroundColor: Colors.white),
                  ),
                OutlinedButton.icon(
                  onPressed: () => _showEscalateDialog(context, caseProv, c.id),
                  icon: const Icon(Icons.warning, size: 14, color: AssistIQTheme.error),
                  label: Text('Escalate L2', style: GoogleFonts.inter(color: AssistIQTheme.error, fontWeight: FontWeight.bold)),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AssistIQTheme.error),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            const Divider(color: Color(0x3377786C)),
            const SizedBox(height: 10),

            // Message Thread View
            MessageThreadView(caseId: c.id),
          ],
        ),
      ),
    );
  }

  void _showReopenDialog(BuildContext context, CaseProvider caseProv, String caseId) {
    final reasonCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Reopen Case (7-Day SLA Window)', style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold)),
        content: TextField(
          controller: reasonCtrl,
          decoration: AssistIQTheme.liquidInputDecoration(
            labelText: 'Reason for reopening',
          ),
          maxLines: 3,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              if (reasonCtrl.text.trim().isNotEmpty) {
                await caseProv.reopenCase(caseId, reasonCtrl.text.trim());
                if (ctx.mounted) Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.secondary, foregroundColor: Colors.white),
            child: const Text('Reopen Case'),
          ),
        ],
      ),
    );
  }

  void _showEscalateDialog(BuildContext context, CaseProvider caseProv, String caseId) {
    final reasonCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Escalate Case to L2 / TeamLead', style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold)),
        content: TextField(
          controller: reasonCtrl,
          decoration: AssistIQTheme.liquidInputDecoration(
            labelText: 'Escalation rationale',
          ),
          maxLines: 3,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              if (reasonCtrl.text.trim().isNotEmpty) {
                await caseProv.escalateCase(caseId, reasonCtrl.text.trim());
                if (ctx.mounted) Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.error, foregroundColor: Colors.white),
            child: const Text('Escalate'),
          ),
        ],
      ),
    );
  }
}

