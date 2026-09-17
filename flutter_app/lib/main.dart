import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/case_provider.dart';
import 'providers/insights_provider.dart';
import 'screens/login_screen.dart';
import 'screens/workbench_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AssistIQApp());
}

class AssistIQApp extends StatelessWidget {
  const AssistIQApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => CaseProvider()),
        ChangeNotifierProvider(create: (_) => InsightsProvider()),
      ],
      child: MaterialApp(
        title: 'AssistIQ Console',
        debugShowCheckedModeBanner: false,
        theme: AssistIQTheme.lightTheme,
        home: const AuthGate(),
      ),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);

    if (auth.isLoading) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(color: AssistIQTheme.primary),
              SizedBox(height: 16),
              Text(
                'Loading AssistIQ Multi-Platform Console...',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AssistIQTheme.primary),
              ),
            ],
          ),
        ),
      );
    }

    if (auth.isAuthenticated) {
      return const WorkbenchScreen();
    } else {
      return const LoginScreen();
    }
  }
}
