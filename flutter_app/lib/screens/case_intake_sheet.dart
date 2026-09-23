import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
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
  String? _errorMessage;
  CaseModel? _createdCase;
  AITriageResultModel? _triageResult;

  static const Map<String, Map<String, dynamic>> _severityInfo = {
    'P1': {
      'label': 'P1 — Critical',
      'sla': '15m Response • 4h Resolve SLA',
      'desc': 'Immediate critical stoppage / severe hazard. Unusable core operational equipment.',
      'color': AssistIQTheme.error,
    },
    'P2': {
      'label': 'P2 — High',
      'sla': '1h Response • 8h Resolve SLA',
      'desc': 'Major component impairment. Heavy performance loss with limited workaround.',
      'color': AssistIQTheme.secondary,
    },
    'P3': {
      'label': 'P3 — Medium',
      'sla': '4h Response • 72h Resolve SLA',
      'desc': 'Normal operational issue with viable workaround. Routine incident.',
      'color': AssistIQTheme.primary,
    },
    'P4': {
      'label': 'P4 — Low',
      'sla': '24h Response • 120h Resolve SLA',
      'desc': 'Minor cosmetic issue, general inquiry, or standard non-blocking service request.',
      'color': AssistIQTheme.tertiary,
    },
  };

  Future<void> _submitDocket() async {
    final title = _titleCtrl.text.trim();
    final desc = _descCtrl.text.trim();

    if (title.length < 3) {
      setState(() => _errorMessage = 'Docket Title must be at least 3 characters.');
      return;
    }
    if (desc.length < 5) {
      setState(() => _errorMessage = 'Problem statement must be at least 5 characters.');
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final caseProv = Provider.of<CaseProvider>(context, listen: false);
      final newCase = await caseProv.createCase(
        title: title,
        description: desc,
        caseType: _caseType,
        category: _category,
        priority: _priority,
        site: _siteCtrl.text.trim(),
      );

      if (!mounted) return;
      setState(() => _createdCase = newCase);

      final triage = await caseProv.getTriage(newCase.id);
      if (mounted) {
        setState(() => _triageResult = triage);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
        });
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final sev = _severityInfo[_priority] ?? _severityInfo['P3']!;
    final Color sevColor = sev['color'] as Color;

    return SafeArea(
      child: Padding(
        padding: EdgeInsets.only(bottom: bottomInset),
        child: Container(
          decoration: AssistIQTheme.liquidGlassElevatedDecoration(
            radius: 24,
            baseColor: AssistIQTheme.surfaceContainerLowest,
          ),
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                // Drag handle bar
                Center(
                  child: Container(
                    width: 36,
                    height: 4,
                    decoration: BoxDecoration(
                      color: AssistIQTheme.outlineVariant.withValues(alpha: 0.6),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // Header Bar
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: AssistIQTheme.primaryContainer.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Icon(Icons.psychology, color: AssistIQTheme.primary, size: 20),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          'NEW DOCKET // AI TRIAGE INTAKE',
                          style: GoogleFonts.outfit(fontSize: 13, fontWeight: FontWeight.bold, letterSpacing: 0.6, color: AssistIQTheme.onSurface),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 20),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const Divider(color: Color(0x2277786C)),
                const SizedBox(height: 8),

                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFECEB),
                      border: Border.all(color: AssistIQTheme.error.withValues(alpha: 0.4)),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: AssistIQTheme.error, size: 16),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(fontSize: 11, color: AssistIQTheme.error, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                ],

                if (_createdCase == null) ...[
                  TextField(
                    controller: _titleCtrl,
                    style: GoogleFonts.inter(fontSize: 13, color: AssistIQTheme.onSurface),
                    decoration: InputDecoration(
                      labelText: 'DOCKET TITLE / SUMMARY',
                      labelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                      filled: true,
                      fillColor: AssistIQTheme.surfaceContainerLowest,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0x3377786C)),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0x3377786C)),
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                    ),
                  ),
                  const SizedBox(height: 12),

                  TextField(
                    controller: _descCtrl,
                    maxLines: 3,
                    style: GoogleFonts.inter(fontSize: 13, color: AssistIQTheme.onSurface),
                    decoration: InputDecoration(
                      labelText: 'DESCRIPTION',
                      labelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                      filled: true,
                      fillColor: AssistIQTheme.surfaceContainerLowest,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0x3377786C)),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0x3377786C)),
                      ),
                      contentPadding: const EdgeInsets.all(12),
                    ),
                  ),
                  const SizedBox(height: 12),

                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _caseType,
                          dropdownColor: AssistIQTheme.surfaceContainerLowest,
                          style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface),
                          decoration: InputDecoration(
                            labelText: 'TYPE',
                            labelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                              borderSide: const BorderSide(color: Color(0x3377786C)),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                              borderSide: const BorderSide(color: Color(0x3377786C)),
                            ),
                            filled: true,
                            fillColor: AssistIQTheme.surfaceContainerLowest,
                            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                          ),
                          items: ['Incident', 'ServiceRequest']
                              .map((t) => DropdownMenuItem(value: t, child: Text(t == 'ServiceRequest' ? 'Service Req' : t, style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface))))
                              .toList(),
                          onChanged: (val) => setState(() => _caseType = val!),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _category,
                          dropdownColor: AssistIQTheme.surfaceContainerLowest,
                          style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface),
                          decoration: InputDecoration(
                            labelText: 'CATEGORY',
                            labelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                              borderSide: const BorderSide(color: Color(0x3377786C)),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                              borderSide: const BorderSide(color: Color(0x3377786C)),
                            ),
                            filled: true,
                            fillColor: AssistIQTheme.surfaceContainerLowest,
                            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                          ),
                          items: ['Hardware', 'Network', 'Software', 'Industrial Control', 'Security', 'Access Control']
                              .map((c) => DropdownMenuItem(value: c, child: Text(c, maxLines: 1, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface))))
                              .toList(),
                          onChanged: (val) => setState(() => _category = val!),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Severity Selector with full SLA descriptions
                  DropdownButtonFormField<String>(
                    value: _priority,
                    dropdownColor: AssistIQTheme.surfaceContainerLowest,
                    style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface),
                    decoration: InputDecoration(
                      labelText: 'INITIAL SEVERITY / SLA TARGET',
                      labelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0x3377786C)),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0x3377786C)),
                      ),
                      filled: true,
                      fillColor: AssistIQTheme.surfaceContainerLowest,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                    ),
                    items: _severityInfo.entries.map((entry) {
                      return DropdownMenuItem<String>(
                        value: entry.key,
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: entry.value['color'] as Color,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                entry.key,
                                style: GoogleFonts.jetBrainsMono(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${entry.value['label']} (${entry.value['sla']})',
                              style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                    onChanged: (val) => setState(() => _priority = val!),
                  ),
                  const SizedBox(height: 10),

                  // Severity Description Card
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: sevColor.withValues(alpha: 0.08),
                      border: Border.all(color: sevColor.withValues(alpha: 0.3)),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.info_outline, size: 16, color: sevColor),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${sev['label']}: ${sev['sla']}',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: sevColor),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                sev['desc'] as String,
                                style: const TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant, height: 1.3),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),

                  ElevatedButton.icon(
                    onPressed: _isSubmitting ? null : _submitDocket,
                    icon: _isSubmitting
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.psychology, size: 18),
                    label: Text(_isSubmitting ? 'ANALYZING & SUBMITTING...' : 'SUBMIT & RUN AI TRIAGE'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AssistIQTheme.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                    ),
                  ),
                ] else ...[
                  // Post-Creation AI Triage Review Card
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
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                '${_createdCase!.referenceNumber}: ${_createdCase!.title}',
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            const SizedBox(width: 6),
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
                        ] else ...[
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 8),
                            child: Row(
                              children: [
                                SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2)),
                                SizedBox(width: 8),
                                Text('Running AI Triage Analysis...', style: TextStyle(fontSize: 11, fontStyle: FontStyle.italic)),
                              ],
                            ),
                          ),
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
        ),
      ),
    );
  }
}
