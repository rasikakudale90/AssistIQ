import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../models/case_model.dart';
import '../models/triage_model.dart';
import '../providers/case_provider.dart';

class CaseIntakeSheet extends StatefulWidget {
  const CaseIntakeSheet({super.key});

  @override
  State<CaseIntakeSheet> createState() => _CaseIntakeSheetState();
}

class _CaseIntakeSheetState extends State<CaseIntakeSheet> {
  final TextEditingController _titleCtrl = TextEditingController();
  final TextEditingController _descCtrl = TextEditingController();
  final TextEditingController _siteCtrl = TextEditingController(text: 'Substation 4');
  String _category = 'Hardware';
  String _priority = 'P3';
  String _caseType = 'Incident';

  bool _isSubmitting = false;
  CaseModel? _createdCase;
  AITriageResultModel? _triageResult;

  Future<void> _submitDocket() async {
    if (_titleCtrl.text.trim().isEmpty || _descCtrl.text.trim().isEmpty) return;
    setState(() => _isSubmitting = true);

    try {
      final caseProv = Provider.of<CaseProvider>(context, listen: false);
      final newCase = await caseProv.createCase(
        title: _titleCtrl.text.trim(),
        description: _descCtrl.text.trim(),
        caseType: _caseType,
        category: _category,
        priority: _priority,
        site: _siteCtrl.text.trim(),
      );

      setState(() => _createdCase = newCase);

      final triage = await caseProv.getTriage(newCase.id);
      setState(() => _triageResult = triage);
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      constraints: const BoxConstraints(maxHeight: 650),
      decoration: const BoxDecoration(
        color: AssistIQTheme.surface,
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.between,
              children: [
                const Row(
                  children: [
                    Icon(Icons.psychology, color: AssistIQTheme.primary),
                    SizedBox(width: 8),
                    Text(
                      'NEW DOCKET // AI TRIAGE INTAKE',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const Divider(),
            const SizedBox(height: 10),

            if (_createdCase == null) ...[
              TextField(
                controller: _titleCtrl,
                decoration: const InputDecoration(
                  labelText: 'DOCKET TITLE / SUMMARY',
                  labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                ),
              ),
              const SizedBox(height: 10),

              TextField(
                controller: _descCtrl,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: 'STATEMENT & SYMPTOMS',
                  labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.all(10),
                ),
              ),
              const SizedBox(height: 10),

              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _category,
                      decoration: const InputDecoration(
                        labelText: 'CATEGORY',
                        border: OutlineInputBorder(),
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      ),
                      items: ['Hardware', 'Network', 'Software', 'Industrial Control', 'Security']
                          .map((c) => DropdownMenuItem(value: c, child: Text(c, style: const TextStyle(fontSize: 12))))
                          .toList(),
                      onChanged: (val) => setState(() => _category = val!),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _priority,
                      decoration: const InputDecoration(
                        labelText: 'SEVERITY',
                        border: OutlineInputBorder(),
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      ),
                      items: ['P1', 'P2', 'P3', 'P4']
                          .map((p) => DropdownMenuItem(value: p, child: Text(p, style: const TextStyle(fontSize: 12))))
                          .toList(),
                      onChanged: (val) => setState(() => _priority = val!),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              ElevatedButton.icon(
                onPressed: _isSubmitting ? null : _submitDocket,
                icon: const Icon(Icons.psychology, size: 18),
                label: Text(_isSubmitting ? 'ANALYZING & SUBMITTING...' : 'SUBMIT & RUN AI TRIAGE'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AssistIQTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                ),
              ),
            ] else ...[
              // Post-Creation AI Triage Review Card (Matching Stitch Screen 1 & 2)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: const Color(0x33C7C7B9)),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        Text(
                          '${_createdCase!.referenceNumber}: ${_createdCase!.title}',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AssistIQTheme.primary,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            _createdCase!.status,
                            style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    if (_triageResult != null) ...[
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'AI TRIAGE ASSESSMENT [SRS §5.2]',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.primary),
                          ),
                          Text(
                            'CONFIDENCE: ${(_triageResult!.confidenceScore * 100).toInt()}%',
                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.primaryContainer),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),

                      Text('Recommended Category: ${_triageResult!.predictedCategory}', style: const TextStyle(fontSize: 12)),
                      Text('Predicted Priority: [${_triageResult!.predictedPriority}]', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AssistIQTheme.secondary)),
                      const SizedBox(height: 8),

                      if (_triageResult!.supportingFactors.isNotEmpty) ...[
                        const Text('Supporting Telemetry Factors:', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.tertiary)),
                        ..._triageResult!.supportingFactors.map((f) => Text('• $f', style: const TextStyle(fontSize: 11))),
                      ],
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 12),

              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AssistIQTheme.primary,
                  foregroundColor: Colors.white,
                ),
                child: const Text('GO TO WORKBENCH'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
