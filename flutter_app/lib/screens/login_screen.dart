import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailCtrl = TextEditingController();
  final TextEditingController _passCtrl = TextEditingController();
  String? _errorMessage;

  final List<Map<String, String>> demoRoles = [
    {
      'role': 'Requester',
      'title': 'Field Requester',
      'email': 'requester@assistiq.local',
      'desc': 'Submit incidents, track status, view public notes',
    },
    {
      'role': 'Operator',
      'title': 'Tier 1 Operator',
      'email': 'operator@assistiq.local',
      'desc': 'Triage workbench, internal notes, AI draft assistance',
    },
    {
      'role': 'TeamLead',
      'title': 'Support Team Lead',
      'email': 'lead@assistiq.local',
      'desc': 'Queue routing, SLA monitoring, escalations',
    },
    {
      'role': 'Manager',
      'title': 'IT Helpdesk Manager',
      'email': 'manager@assistiq.local',
      'desc': 'Operational insights, AI narrative, CSV reports',
    },
    {
      'role': 'Administrator',
      'title': 'System Administrator',
      'email': 'admin@assistiq.local',
      'desc': 'Full RBAC, team administration, audit trails',
    },
  ];

  Future<void> _handleLogin() async {
    setState(() => _errorMessage = null);
    try {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      await auth.login(_emailCtrl.text.trim(), _passCtrl.text.trim());
    } catch (e) {
      setState(() => _errorMessage = e.toString().replaceAll('Exception: ', ''));
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 440),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AssistIQTheme.surfaceContainerLow,
              border: Border.all(color: const Color(0x33C7C7B9)),
              borderRadius: BorderRadius.circular(12),
              boxShadow: const [
                BoxShadow(color: Color(0x0A000000), blurRadius: 16, offset: Offset(0, 4)),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Brand Header
                Center(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AssistIQTheme.primary,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'AI',
                      style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Center(
                  child: Text(
                    'AssistIQ IT Helpdesk',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
                const Center(
                  child: Text(
                    'MW-OS // MULTI-PLATFORM CLIENT',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2, color: AssistIQTheme.primary),
                  ),
                ),
                const SizedBox(height: 20),

                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AssistIQTheme.errorContainer,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(fontSize: 12, color: AssistIQTheme.error),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                TextField(
                  controller: _emailCtrl,
                  decoration: const InputDecoration(
                    labelText: 'EMAIL ADDRESS',
                    labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  ),
                ),
                const SizedBox(height: 12),

                TextField(
                  controller: _passCtrl,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'PASSWORD',
                    labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  ),
                ),
                const SizedBox(height: 16),

                ElevatedButton(
                  onPressed: auth.isLoading ? null : _handleLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AssistIQTheme.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                  ),
                  child: auth.isLoading
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('SIGN IN', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.0)),
                ),

                const SizedBox(height: 24),
                const Divider(),
                const SizedBox(height: 12),

                // 1-Click Demo Personas
                const Row(
                  children: [
                    Icon(Icons.vpn_key_outlined, size: 16, color: AssistIQTheme.primary),
                    SizedBox(width: 6),
                    Text(
                      'INSTANT 1-CLICK DEMO PERSONAS',
                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.primary, letterSpacing: 0.8),
                    ),
                  ],
                ),
                const SizedBox(height: 10),

                ...demoRoles.map(
                  (d) => Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: InkWell(
                      onTap: auth.isLoading ? null : () => auth.switchDemoRole(d['role']!),
                      borderRadius: BorderRadius.circular(6),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          border: Border.all(color: const Color(0x33C7C7B9)),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(d['title']!, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                      const SizedBox(width: 4),
                                      Text('[${d['role']!}]', style: const TextStyle(fontSize: 10, color: AssistIQTheme.primary, fontWeight: FontWeight.bold)),
                                    ],
                                  ),
                                  Text(d['desc']!, style: const TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant)),
                                ],
                              ),
                            ),
                            const Icon(Icons.arrow_forward_ios, size: 12, color: AssistIQTheme.onSurfaceVariant),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
