import 'package:flutter/material.dart';
import 'ui/core/theme.dart';
import 'ui/core/theme_notifier.dart';
import 'ui/features/navigation/app_scaffold.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SmmsApplication());
}

class SmmsApplication extends StatefulWidget {
  const SmmsApplication({super.key});

  @override
  State<SmmsApplication> createState() => _SmmsApplicationState();
}

class _SmmsApplicationState extends State<SmmsApplication> {
  final ThemeNotifier _themeNotifier = ThemeNotifier();

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _themeNotifier,
      builder: (context, _) {
        return MaterialApp(
          title: 'SMMS Tanzania - Civil Infrastructure Health Monitoring',
          debugShowCheckedModeBanner: false,
          themeMode: _themeNotifier.themeMode, // Follows device theme mode by default
          theme: CivilEngineeringTheme.lightTheme,
          darkTheme: CivilEngineeringTheme.darkTheme,
          home: AppScaffold(themeNotifier: _themeNotifier),
        );
      },
    );
  }
}
