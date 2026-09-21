import 'package:flutter/material.dart';
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
      const NavigationDestination(icon: Icon(Icons.table_rows), label: 'Workbench'),
      if (isStaff) const NavigationDestination(icon: Icon(Icons.query_stats), label: 'Insights'),
      if (isStaff) const NavigationDestination(icon: Icon(Icons.notifications_active), label: 'Dispatch'),
      const NavigationDestination(icon: Icon(Icons.menu_book), label: 'Knowledge'),
      if (isStaff) const NavigationDestination(icon: Icon(Icons.admin_panel_settings), label: 'Admin'),
    ];

    return Scaffold(
      appBar: const AppHeader(title: 'Field Operations Console'),
      body: _buildCurrentTab(context),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentNavIndex,
        onDestinationSelected: (idx) => setState(() => _currentNavIndex = idx),
        destinations: navDestinations,
      ),
      floatingActionButton: _currentNavIndex == 0
          ? FloatingActionButton.extended(
              onPressed: () {
                showModalBottomSheet(
                  context: context,
                  isScrollControlled: true,
                  builder: (_) => const CaseIntakeSheet(),
                );
              },
              icon: const Icon(Icons.add_circle, color: Colors.white),
              label: const Text('NEW INTAKE', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              backgroundColor: AssistIQTheme.primary,
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
                width: 360,
                child: _buildQueueList(context),
              ),
              const VerticalDivider(width: 1),
              Expanded(
                child: selected != null
                    ? _buildDetailPane(context, selected)
                    : const Center(child: Text('Select a docket to view details')),
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
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: ['ALL', 'ACTIVE', 'BREACHED', 'UNASSIGNED'].map((f) {
                final isSel = caseProv.filter == f;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(f, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isSel ? Colors.white : null)),
                    selected: isSel,
                    selectedColor: AssistIQTheme.primary,
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
              ? const Center(child: CircularProgressIndicator())
              : filtered.isEmpty
                  ? const Center(child: Text('No cases matching filter'))
                  : ListView.builder(
                      itemCount: filtered.length,
                      itemBuilder: (context, index) {
                        final c = filtered[index];
                        final isSel = caseProv.selectedCase?.id == c.id;

                        return Card(
                          margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          color: isSel ? AssistIQTheme.surfaceContainerHigh : Colors.white,
                          child: ListTile(
                            onTap: () {
                              caseProv.selectCase(c);
                              if (MediaQuery.of(context).size.width <= 800) {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => Scaffold(
                                      appBar: AppBar(title: Text(c.referenceNumber)),
                                      body: SingleChildScrollView(child: _buildDetailPane(context, c)),
                                    ),
                                  ),
                                );
                              }
                            },
                            title: Row(
                              children: [
                                Text('#${c.referenceNumber}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AssistIQTheme.primary)),
                                const SizedBox(width: 6),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: c.priority == 'P1' ? AssistIQTheme.error : AssistIQTheme.secondary,
                                    borderRadius: BorderRadius.circular(3),
                                  ),
                                  child: Text(c.priority, style: const TextStyle(fontSize: 9, color: Colors.white, fontWeight: FontWeight.bold)),
                                ),
                              ],
                            ),
                            subtitle: Text(c.title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12)),
                            trailing: Text(c.status, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  '#${c.referenceNumber} — ${c.title}',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: AssistIQTheme.primary, borderRadius: BorderRadius.circular(4)),
                child: Text(c.status, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(c.description, style: const TextStyle(fontSize: 13, height: 1.4)),
          const SizedBox(height: 12),

          // SLA Card
          SLACountdownCard(sla: c.sla, priority: c.priority),
          const SizedBox(height: 12),

          // Status Transition Quick Buttons
          Wrap(
            spacing: 8,
            children: [
              if (c.status == 'New')
                ElevatedButton(
                  onPressed: () => caseProv.updateStatus(c.id, 'InAssessment', c.version),
                  style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.primary, foregroundColor: Colors.white),
                  child: const Text('Start Assessment'),
                ),
              if (c.status == 'InAssessment')
                ElevatedButton(
                  onPressed: () => caseProv.updateStatus(c.id, 'Assigned', c.version),
                  style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.primary, foregroundColor: Colors.white),
                  child: const Text('Assign Case'),
                ),
              if (c.status == 'Assigned')
                ElevatedButton(
                  onPressed: () => caseProv.updateStatus(c.id, 'Resolved', c.version),
                  style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.primary, foregroundColor: Colors.white),
                  child: const Text('Mark Resolved'),
                ),
              if (c.status == 'Resolved') ...[
                ElevatedButton(
                  onPressed: () => caseProv.updateStatus(c.id, 'Closed', c.version),
                  style: ElevatedButton.styleFrom(backgroundColor: AssistIQTheme.primary, foregroundColor: Colors.white),
                  child: const Text('Confirm Fix & Close'),
                ),
                OutlinedButton(
                  onPressed: () => caseProv.updateStatus(c.id, 'Assigned', c.version),
                  style: OutlinedButton.styleFrom(foregroundColor: AssistIQTheme.secondary),
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
                label: const Text('Escalate L2', style: TextStyle(color: AssistIQTheme.error)),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 8),

          // Message Thread View
          MessageThreadView(caseId: c.id),
        ],
      ),
    );
  }

  void _showReopenDialog(BuildContext context, CaseProvider caseProv, String caseId) {
    final reasonCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Reopen Case (7-Day SLA Window)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        content: TextField(
          controller: reasonCtrl,
          decoration: const InputDecoration(
            labelText: 'Reason for reopening',
            border: OutlineInputBorder(),
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
        title: const Text('Escalate Case to L2 / TeamLead', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        content: TextField(
          controller: reasonCtrl,
          decoration: const InputDecoration(
            labelText: 'Escalation rationale',
            border: OutlineInputBorder(),
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

