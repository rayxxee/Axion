import 'package:flutter/material.dart';
import 'screens/input_screen.dart';

void main() {
  runApp(const AxionApp());
}

class AxionApp extends StatelessWidget {
  const AxionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Axion',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurpleAccent,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const InputScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
