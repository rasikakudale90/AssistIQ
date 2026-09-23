import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../providers/auth_provider.dart';

class AdminScreen extends StatelessWidget {
  const AdminScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.user;

    final users = [
      {'email': 'requester@assistiq.local', 'role': 'Requester', 'team': 'Field Operations'},
      {'email': 'operator@assistiq.local', 'role': 'Operator', 'team': 'Tier 1 Support'},
      {'email': 'lead@assistiq.local', 'role': 'TeamLead', 'team': 'Application Support'},
      {'email': 'manager@assistiq.local', 'role': 'Manager', 'team': 'Operations Management'},
      {'email': 'admin@assistiq.local', 'role': 'Administrator', 'team': 'System Administration'},
    ];

    return AmbientBackground(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // User Profile Card
            if (user != null)
              Container(
                decoration: AssistIQTheme.liquidGlassElevatedDecoration(radius: 16),
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AssistIQTheme.primary,
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: [
                          BoxShadow(
                            color: AssistIQTheme.primary.withValues(alpha: 0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          user.email[0].toUpperCase(),
                          style: GoogleFonts.outfit(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(user.email, style: GoogleFonts.outfit(fontSize: 15, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface)),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AssistIQTheme.primaryContainer.withValues(alpha: 0.15),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(user.role, style: GoogleFonts.jetBrainsMono(fontSize: 10, color: AssistIQTheme.primary, fontWeight: FontWeight.bold)),
                              ),
                              const SizedBox(width: 6),
                              Text('• Active & Verified', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.primary, fontWeight: FontWeight.w600)),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 16),

            // User Directory & RBAC Table
            Container(
              decoration: AssistIQTheme.liquidGlassDecoration(radius: 16),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.manage_accounts, size: 18, color: AssistIQTheme.primary),
                      const SizedBox(width: 8),
                      Text('RBAC USER DIRECTORY', style: GoogleFonts.outfit(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.6, color: AssistIQTheme.onSurface)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ...users.map(
                    (u) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(u['email']!, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface)),
                                Text(u['team']!, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 10, color: AssistIQTheme.onSurfaceVariant)),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                            decoration: BoxDecoration(
                              color: AssistIQTheme.surfaceContainerHigh,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(u['role']!, style: GoogleFonts.jetBrainsMono(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.primary)),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // System Architecture Overview
            Container(
              decoration: AssistIQTheme.liquidGlassDecoration(
                radius: 16,
                baseColor: AssistIQTheme.surfaceContainerLow.withValues(alpha: 0.9),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.memory, size: 18, color: AssistIQTheme.primary),
                      const SizedBox(width: 8),
                      Text('SYSTEM SPECIFICATION', style: GoogleFonts.outfit(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.primary, letterSpacing: 0.5)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('• Backend: FastAPI (Python 3.14) with APScheduler Background Sweep', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.onSurface, height: 1.4)),
                  Text('• Database: PostgreSQL 16 + pg_trgm similarity search (Supabase)', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.onSurface, height: 1.4)),
                  Text('• AI Provider: Google Gemini 2.5 Flash Triage Engine', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.onSurface, height: 1.4)),
                  Text('• Client: Flutter Multi-Target (Android, iOS, Web, Windows)', style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.onSurface, height: 1.4)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
