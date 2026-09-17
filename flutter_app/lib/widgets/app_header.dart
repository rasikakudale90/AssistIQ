import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../providers/auth_provider.dart';

class AppHeader extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  const AppHeader({super.key, this.title = 'AssistIQ Workbench'});

  @override
  Size get preferredSize => const Size.fromHeight(60);

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.user;

    return AppBar(
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AssistIQTheme.primary,
              borderRadius: BorderRadius.circular(4),
            ),
            child: const Text(
              'AI',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'MW-OS // HELPDESK',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  color: AssistIQTheme.primary,
                ),
              ),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        if (user != null)
          PopupMenuButton<String>(
            tooltip: 'Switch Persona / Role',
            onSelected: (role) {
              if (role == 'LOGOUT') {
                auth.logout();
              } else {
                auth.switchDemoRole(role);
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                enabled: false,
                child: Text(
                  'DEMO PERSONA SWITCHER',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
              ...['Requester', 'Operator', 'TeamLead', 'Manager', 'Administrator'].map(
                (r) => PopupMenuItem(
                  value: r,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Text(r, style: TextStyle(
                        fontWeight: user.role == r ? FontWeight.bold : FontWeight.normal,
                        color: user.role == r ? AssistIQTheme.primary : null,
                      )),
                      if (user.role == r)
                        const Icon(Icons.check, size: 16, color: AssistIQTheme.primary),
                    ],
                  ),
                ),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem(
                value: 'LOGOUT',
                child: Row(
                  children: [
                    Icon(Icons.logout, size: 16, color: AssistIQTheme.error),
                    SizedBox(width: 8),
                    Text('Log out', style: TextStyle(color: AssistIQTheme.error)),
                  ],
                ),
              ),
            ],
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Row(
                children: [
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        user.email.split('@').first,
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '[${user.role}]',
                        style: const TextStyle(
                          fontSize: 10,
                          color: AssistIQTheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    radius: 14,
                    backgroundColor: AssistIQTheme.primary,
                    child: Text(
                      user.role[0],
                      style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
