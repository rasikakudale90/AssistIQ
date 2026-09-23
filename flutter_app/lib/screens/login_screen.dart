import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
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

    if (_emailCtrl.text.trim().isEmpty || _passCtrl.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter your email and password.');
      return;
    }

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

    if (_regEmailCtrl.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a valid work email.');
      return;
    }

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
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.cloud_sync, color: AssistIQTheme.primary, size: 22),
            const SizedBox(width: 8),
            Text(
              'Backend API Server',
              style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Specify the backend endpoint (e.g. Render production or local dev):',
              style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurfaceVariant),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: urlCtrl,
              decoration: AssistIQTheme.liquidInputDecoration(
                labelText: 'API BASE URL',
                hintText: 'https://assistiq-si1f.onrender.com/api/v1',
              ),
              style: GoogleFonts.jetBrainsMono(fontSize: 12),
            ),
            const SizedBox(height: 12),
            Text(
              'QUICK PRESETS:',
              style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.outline),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                ActionChip(
                  backgroundColor: AssistIQTheme.primary.withValues(alpha: 0.1),
                  side: const BorderSide(color: AssistIQTheme.primary),
                  label: Text('☁️ Cloud Live', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.primary)),
                  onPressed: () => urlCtrl.text = 'https://assistiq-si1f.onrender.com/api/v1',
                ),
                ActionChip(
                  label: Text('📱 Wi-Fi LAN', style: GoogleFonts.inter(fontSize: 11)),
                  onPressed: () => urlCtrl.text = 'http://10.29.182.168:8000/api/v1',
                ),
                ActionChip(
                  label: Text('🤖 Emulator', style: GoogleFonts.inter(fontSize: 11)),
                  onPressed: () => urlCtrl.text = 'http://10.0.2.2:8000/api/v1',
                ),
                ActionChip(
                  label: Text('💻 Localhost', style: GoogleFonts.inter(fontSize: 11)),
                  onPressed: () => urlCtrl.text = 'http://127.0.0.1:8000/api/v1',
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text('CANCEL', style: GoogleFonts.inter(fontWeight: FontWeight.bold)),
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
            child: Text('SAVE & CONNECT', style: GoogleFonts.inter(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      body: AmbientBackground(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 28),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 440),
              padding: const EdgeInsets.all(24),
              decoration: AssistIQTheme.liquidGlassElevatedDecoration(radius: 20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Brand Header with Glowing Liquid Accent
                  Center(
                    child: Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [AssistIQTheme.primary, AssistIQTheme.primaryContainer],
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: AssistIQTheme.primary.withValues(alpha: 0.35),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Text(
                          'AI',
                          style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: -0.5),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Center(
                    child: Text(
                      'AssistIQ Enterprise',
                      style: GoogleFonts.outfit(fontSize: 22, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AssistIQTheme.primary.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AssistIQTheme.primary.withValues(alpha: 0.25)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 6,
                            height: 6,
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.green,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'ENTERPRISE MULTI-PLATFORM v1.0.0',
                            style: GoogleFonts.jetBrainsMono(
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.8,
                              color: AssistIQTheme.primary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Tab Switcher (SIGN IN / REGISTER)
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: AssistIQTheme.surfaceContainerLow,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0x3377786C)),
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
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              padding: const EdgeInsets.symmetric(vertical: 9),
                              decoration: BoxDecoration(
                                color: _authTab == 0 ? AssistIQTheme.primary : Colors.transparent,
                                borderRadius: BorderRadius.circular(9),
                                boxShadow: _authTab == 0
                                    ? [
                                        BoxShadow(
                                          color: AssistIQTheme.primary.withValues(alpha: 0.3),
                                          blurRadius: 8,
                                          offset: const Offset(0, 2),
                                        ),
                                      ]
                                    : null,
                              ),
                              child: Center(
                                child: Text(
                                  'SIGN IN',
                                  style: GoogleFonts.inter(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    letterSpacing: 0.5,
                                    color: _authTab == 0 ? AssistIQTheme.onPrimary : AssistIQTheme.outline,
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
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              padding: const EdgeInsets.symmetric(vertical: 9),
                              decoration: BoxDecoration(
                                color: _authTab == 1 ? AssistIQTheme.primary : Colors.transparent,
                                borderRadius: BorderRadius.circular(9),
                                boxShadow: _authTab == 1
                                    ? [
                                        BoxShadow(
                                          color: AssistIQTheme.primary.withValues(alpha: 0.3),
                                          blurRadius: 8,
                                          offset: const Offset(0, 2),
                                        ),
                                      ]
                                    : null,
                              ),
                              child: Center(
                                child: Text(
                                  'REGISTER ACCOUNT',
                                  style: GoogleFonts.inter(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    letterSpacing: 0.5,
                                    color: _authTab == 1 ? AssistIQTheme.onPrimary : AssistIQTheme.outline,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  if (_errorMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AssistIQTheme.errorContainer,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AssistIQTheme.error.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline, color: AssistIQTheme.error, size: 18),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _errorMessage!,
                              style: GoogleFonts.inter(color: AssistIQTheme.error, fontSize: 12, fontWeight: FontWeight.w600),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),
                  ],

                  if (_successMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFD4EDDA),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: const Color(0xFF28A745).withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_outline, color: Color(0xFF155724), size: 18),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _successMessage!,
                              style: GoogleFonts.inter(color: const Color(0xFF155724), fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),
                  ],

                  if (_authTab == 0) ...[
                    // Sign In Fields
                    TextField(
                      controller: _emailCtrl,
                      decoration: AssistIQTheme.liquidInputDecoration(
                        labelText: 'WORK EMAIL',
                        hintText: 'operator@assistiq.local',
                        prefixIcon: const Icon(Icons.mail_outline, size: 18, color: AssistIQTheme.outline),
                      ),
                      keyboardType: TextInputType.emailAddress,
                      style: GoogleFonts.inter(fontSize: 13),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _passCtrl,
                      obscureText: true,
                      decoration: AssistIQTheme.liquidInputDecoration(
                        labelText: 'PASSWORD',
                        hintText: '••••••••••••',
                        prefixIcon: const Icon(Icons.lock_outline, size: 18, color: AssistIQTheme.outline),
                      ),
                      style: GoogleFonts.inter(fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: auth.isLoading ? null : _handleLogin,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AssistIQTheme.primary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        elevation: 2,
                      ),
                      child: auth.isLoading
                          ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : Text('SIGN IN TO CONSOLE', style: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 0.8, fontSize: 12)),
                    ),
                    const SizedBox(height: 18),
                    const Divider(color: Color(0x33C7C7B9)),
                    const SizedBox(height: 10),

                    // Demo Quick-Switch Roles
                    Text(
                      'QUICK DEMO PERSONA ACCESS:',
                      style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurfaceVariant, letterSpacing: 0.8),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: [
                        _buildDemoRoleButton('Requester', 'Requester', Colors.blueGrey, auth),
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
                      decoration: AssistIQTheme.liquidInputDecoration(
                        labelText: 'ORGANIZATION EMAIL',
                        hintText: 'jane.smith@enterprise.com',
                        prefixIcon: const Icon(Icons.badge_outlined, size: 18, color: AssistIQTheme.outline),
                      ),
                      keyboardType: TextInputType.emailAddress,
                      style: GoogleFonts.inter(fontSize: 13),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _regPassCtrl,
                      obscureText: true,
                      decoration: AssistIQTheme.liquidInputDecoration(
                        labelText: 'PASSWORD (MIN 12 CHARS)',
                        hintText: '••••••••••••',
                        prefixIcon: const Icon(Icons.key, size: 18, color: AssistIQTheme.outline),
                      ),
                      style: GoogleFonts.inter(fontSize: 13),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: _regRole,
                            dropdownColor: AssistIQTheme.surfaceContainerLowest,
                            decoration: AssistIQTheme.liquidInputDecoration(
                              labelText: 'INITIAL ROLE',
                            ),
                            style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface),
                            items: ['Requester', 'Operator', 'TeamLead', 'Manager', 'Administrator']
                                .map((r) => DropdownMenuItem(value: r, child: Text(r, style: GoogleFonts.inter(fontSize: 12, color: AssistIQTheme.onSurface))))
                                .toList(),
                            onChanged: (val) => setState(() => _regRole = val!),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: TextField(
                            controller: _regSiteCtrl,
                            decoration: AssistIQTheme.liquidInputDecoration(
                              labelText: 'SITE / REGION',
                            ),
                            style: GoogleFonts.inter(fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: auth.isLoading ? null : _handleRegister,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AssistIQTheme.secondary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        elevation: 2,
                      ),
                      child: auth.isLoading
                          ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : Text('CREATE ENTERPRISE ACCOUNT', style: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 0.8, fontSize: 12)),
                    ),
                  ],

                  // Server Status & Quick Switch Footer
                  const SizedBox(height: 18),
                  Center(
                    child: InkWell(
                      onTap: _showServerConfigDialog,
                      borderRadius: BorderRadius.circular(20),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.8),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0x3377786C)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.green,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              AppConstants.apiBaseUrl.contains('onrender.com')
                                  ? 'Connected: Render Cloud'
                                  : 'Server: ${AppConstants.apiBaseUrl.replaceAll('/api/v1', '')}',
                              style: GoogleFonts.jetBrainsMono(fontSize: 10, color: AssistIQTheme.onSurfaceVariant),
                            ),
                            const SizedBox(width: 6),
                            const Icon(Icons.settings, size: 12, color: AssistIQTheme.primary),
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
      ),
    );
  }

  Widget _buildDemoRoleButton(String role, String label, Color color, AuthProvider auth) {
    return ActionChip(
      avatar: CircleAvatar(backgroundColor: color, radius: 5),
      label: Text(label, style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600)),
      backgroundColor: Colors.white.withValues(alpha: 0.85),
      side: const BorderSide(color: Color(0x3377786C)),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      onPressed: auth.isLoading ? null : () => auth.switchDemoRole(role),
    );
  }
}
