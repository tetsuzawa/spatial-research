import 'package:flutter/material.dart';


import 'angle_sender.dart';
import 'settings.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Welcome to Flutter',
      initialRoute: '/',
      routes: {
        '/': (_) => AngleSender(),
        '/settings': (_) => Settings(),
      },
    );
  }
}

