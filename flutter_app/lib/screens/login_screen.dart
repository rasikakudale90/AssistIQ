import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../core/api_client.dart';
import '../core/constants.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  int _authTab = 0; // 0: Sign In, 1: Register
  final TextEditingController _emailCtrl = TextEditingController();
  final TextEditingController _passCtrl = TextEditingController();

  // Register Fields
  final TextEditingController _regEmailCtrl = TextEditingController();
  final TextEditingController _regPassCtrl = TextEditingController();
  final TextEditingController _regSiteCtrl = TextEditingController(text: 'Main Facility');
  String _regRole = 'Requester';

  String? _errorMessage;
  String? _successMessage;

  Future<void> _handleLogin() async {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
    });
    try {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      await auth.login(_emailCtrl.text.trim(), _passCtrl.text.trim());
    } catch (e) {
      setState(() => _errorMessage = e.toString().replaceAll('Exception: ', ''));
    }
  }

  Future<void> _handleRegister() async {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
    });

    if (_regPassCtrl.text.trim().length < 12) {
      setState(() => _errorMessage = 'Password must be at least 12 characters per enterprise policy.');
      return;
    }

    try {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      await auth.signup(
        _regEmailCtrl.text.trim(),
        _regPassCtrl.text.trim(),
        _regRole,
        _regSiteCtrl.text.trim(),
      );
      setState(() {
        _successMessage = 'Account created successfully! Signed in.';
      });
    } catch (e) {
      setState(() => _errorMessage = e.toString().replaceAll('Exception: ', ''));
    }
  }

  Future<void> _showServerConfigDialog() async {
    final currentUrl = await ApiClient.getBaseUrl();
    final urlCtrl = TextEditingController(text: currentUrl);

    if (!mounted) return;
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.dns, color: AssistIQTheme.primary, size: 20),
            SizedBox(width: 8),
            Text('Server Configuration', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter the backend API base URL (including /api/v1):',
              style: TextStyle(fontSize: 12, color: AssistIQTheme.onSurfaceVariant),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: urlCtrl,
              decoration: const InputDecoration(
                labelText: 'API BASE URL',
                hintText: 'http://10.122.120.196:8000/api/v1',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              ),
              style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 6,
              children: [
                ActionChip(
                  label: const Text('Wi-Fi LAN', style: TextStyle(fontSize: 10)),
                  onPressed: () => urlCtrl.text = 'http://10.122.120.196:8000/api/v1',
                ),
                ActionChip(
                  label: const Text('Emulator', style: TextStyle(fontSize: 10)),
                  onPressed: () => urlCtrl.text = 'http://10.0.2.2:8000/api/v1',
                ),
                ActionChip(
                  label: const Text('Localhost', style: TextStyle(fontSize: 10)),
                  onPressed: () => urlCtrl.text = 'http://127.0.0.1:8000/api/v1',
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('CANCEL'),
          ),
          ElevatedButton(
            onPressed: () async {
              final newUrl = urlCtrl.text.trim();
              if (newUrl.isNotEmpty) {
                await ApiClient.setBaseUrl(newUrl);
                setState(() {});
              }
              if (ctx.mounted) Navigator.of(ctx).pop();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AssistIQTheme.primary,
              foregroundColor: Colors.white,
            ),
            child: const Text('SAVE & CONNECT'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 440),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AssistIQTheme.surfaceContainerLow,
              border: Border.all(color: const Color(0x33C7C7B9)),
              borderRadius: BorderRadius.circular(16),
              boxShadow: const [
                BoxShadow(color: Color(0x0A000000), blurRadius: 20, offset: Offset(0, 6)),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Brand Header
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: AssistIQTheme.primary,
                      borderRadius: BorderRadius.circular(12),
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
                    'AssistIQ Enterprise Helpdesk',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(height: 4),
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AssistIQTheme.primaryContainer.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text(
                      'MW-OS // ENTERPRISE MULTI-PLATFORM',
                      style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, letterSpacing: 1.0, color: AssistIQTheme.primary),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Tab Switcher (SIGN IN / REGISTER)
                Container(
                  padding: const EdgeInsets.all(3),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0x33C7C7B9)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: GestureDetector(
                          onTap: () => setState(() {
                            _authTab = 0;
                            _errorMessage = null;
                            _successMessage = null;
                          }),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: _authTab == 0 ? AssistIQTheme.primary : Colors.transparent,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Center(
                              child: Text(
                                'SIGN IN',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: _authTab == 0 ? Colors.white : AssistIQTheme.onSurfaceVariant,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      Expanded(
                        child: GestureDetector(
                          onTap: () => setState(() {
                            _authTab = 1;
                            _errorMessage = null;
                            _successMessage = null;
                          }),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: _authTab == 1 ? AssistIQTheme.primary : Colors.transparent,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Center(
                              child: Text(
                                'REGISTER ACCOUNT',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: _authTab == 1 ? Colors.white : AssistIQTheme.onSurfaceVariant,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 14),

                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AssistIQTheme.errorContainer,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: AssistIQTheme.error, fontSize: 12),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                if (_successMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFD4EDDA),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _successMessage!,
                      style: const TextStyle(color: Color(0xFF155724), fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                if (_authTab == 0) ...[
                  // Sign In Fields
                  TextField(
                    controller: _emailCtrl,
                    decoration: const InputDecoration(
                      labelText: 'WORK EMAIL',
                      labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      hintText: 'operator@assistiq.local',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _passCtrl,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'PASSWORD',
                      labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      hintText: '••••••••••••',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                  const SizedBox(height: 14),
                  ElevatedButton(
                    onPressed: auth.isLoading ? null : _handleLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AssistIQTheme.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                    ),
                    child: auth.isLoading
                        ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Text('SIGN IN TO CONSOLE', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 0.8, fontSize: 12)),
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: Color(0x33C7C7B9)),
                  const SizedBox(height: 8),

                  // Demo Quick-Switch Roles
                  const Text(
                    'QUICK DEMO ACCESS (1-CLICK):',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant, letterSpacing: 0.8),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [
                      _buildDemoRoleButton('Requester', 'Requester (User)', Colors.blueGrey, auth),
                      _buildDemoRoleButton('Operator', 'Operator (L1)', AssistIQTheme.primary, auth),
                      _buildDemoRoleButton('TeamLead', 'Team Lead (L2)', Colors.indigo, auth),
                      _buildDemoRoleButton('Manager', 'IT Manager', Colors.teal, auth),
                      _buildDemoRoleButton('Administrator', 'Admin', Colors.purple, auth),
                    ],
                  ),
                ] else ...[
                  // Register Account Fields
                  TextField(
                    controller: _regEmailCtrl,
                    decoration: const InputDecoration(
                      labelText: 'ORGANIZATION EMAIL',
                      labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      hintText: 'jane.smith@enterprise.com',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _regPassCtrl,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'PASSWORD (MIN 12 CHARS)',
                      labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      hintText: '••••••••••••',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _regRole,
                          decoration: const InputDecoration(
                            labelText: 'ROLE',
                            border: OutlineInputBorder(),
                            filled: true,
                            fillColor: Colors.white,
                            contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                          ),
                          items: ['Requester', 'Operator', 'TeamLead', 'Manager', 'Administrator']
                              .map((r) => DropdownMenuItem(value: r, child: Text(r, style: const TextStyle(fontSize: 12))))
                              .toList(),
                          onChanged: (val) => setState(() => _regRole = val!),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextField(
                          controller: _regSiteCtrl,
                          decoration: const InputDecoration(
                            labelText: 'FACILITY / SITE',
                            labelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                            filled: true,
                            fillColor: Colors.white,
                            border: OutlineInputBorder(),
                            contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  ElevatedButton(
                    onPressed: auth.isLoading ? null : _handleRegister,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AssistIQTheme.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                    ),
                    child: auth.isLoading
                        ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Text('CREATE ENTERPRISE ACCOUNT', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 0.8, fontSize: 12)),
                  ),
                ],

                // Server Status & Quick Switch Footer
                const SizedBox(height: 16),
                Center(
                  child: InkWell(
                    onTap: _showServerConfigDialog,
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0x33C7C7B9)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.wifi, size: 14, color: Colors.green),
                          const SizedBox(width: 6),
                          Text(
                            'Server: ${AppConstants.apiBaseUrl.replaceAll('/api/v1', '')}',
                            style: const TextStyle(fontSize: 10, fontFamily: 'monospace', color: AssistIQTheme.onSurfaceVariant),
                          ),
                          const SizedBox(width: 4),
                          const Icon(Icons.edit, size: 12, color: AssistIQTheme.primary),
                        ],
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

  Widget _buildDemoRoleButton(String role, String label, Color color, AuthProvider auth) {
    return ActionChip(
      avatar: CircleAvatar(backgroundColor: color, radius: 6),
      label: Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
      backgroundColor: Colors.white,
      side: const BorderSide(color: Color(0x33C7C7B9)),
      onPressed: auth.isLoading ? null : () => auth.switchDemoRole(role),
    );
  }
}
