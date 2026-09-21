import 'package:flutter/material.dart';
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

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // User Profile Card
          if (user != null)
            Card(
              color: Colors.white,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 24,
                      backgroundColor: AssistIQTheme.primary,
                      child: Text(
                        user.email[0].toUpperCase(),
                        style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(user.email, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 2),
                          Text('Role: ${user.role} | Active & Verified', style: const TextStyle(fontSize: 11, color: AssistIQTheme.primary, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 16),

          // User Directory & RBAC Table
          Card(
            color: Colors.white,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('RBAC USER DIRECTORY', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8)),
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
                                Text(u['email']!, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                Text(u['team']!, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, color: AssistIQTheme.onSurfaceVariant)),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(color: AssistIQTheme.surfaceContainerHigh, borderRadius: BorderRadius.circular(4)),
                            child: Text(u['role']!, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AssistIQTheme.primary)),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // System Architecture Overview
          Card(
            color: AssistIQTheme.surfaceContainerLow,
            child: const Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('SYSTEM SPECIFICATION', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AssistIQTheme.primary)),
                  SizedBox(height: 6),
                  Text('• Backend: FastAPI (Python 3.14) with in-process APScheduler Sweep', style: TextStyle(fontSize: 11)),
                  Text('• Database: PostgreSQL 16 + pg_trgm similarity search', style: TextStyle(fontSize: 11)),
                  Text('• AI Provider: Google Gemini 2.5 Flash', style: TextStyle(fontSize: 11)),
                  Text('• Client: Flutter Multi-Target (Android, iOS, Web, Windows, macOS, Linux)', style: TextStyle(fontSize: 11)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
