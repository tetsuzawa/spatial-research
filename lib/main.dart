import 'dart:math';

import 'package:flutter/material.dart';

import 'package:flutter_circular_slider/flutter_circular_slider.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: SafeArea(
          child: Container(
              decoration: BoxDecoration(
                image: DecorationImage(
                  image: AssetImage('images/background_morning.png'),
                  fit: BoxFit.cover,
                ),
              ),
              child: AngleSenderPage()),
        ));
  }
}

class AngleSenderPage extends StatefulWidget {
  @override
  _AngleSenderPageState createState() => _AngleSenderPageState();
}

class _AngleSenderPageState extends State<AngleSenderPage> {
  final baseColor = Color.fromRGBO(255, 255, 255, 0.3);


//  int initAngle;
//  int endAngle;

  int initAngle;
  int endAngle;

  @override
  void initState() {
    super.initState();
    _shuffle();
  }

  void _shuffle() {
    setState(() {
//      initAngle = _generateRandomTime();
//      endAngle = _generateRandomTime();
//      inBedTime = initAngle;
//      outBedTime = endAngle;
      initAngle = 0;
      endAngle = 2;
    });
  }

  void _updateLabels(int init, int end, int laps) {
    setState(() {
      initAngle = init;
      endAngle = end;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Text(
          'How long did you stay in bed?',
          style: TextStyle(color: Colors.white),
        ),
        Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _formatRotation(initAngle, endAngle),
          ],
        ),
        DoubleCircularSlider(
          36,
//          initAngle,
//          endAngle,
          initAngle,
          endAngle,
          height: 260.0,
          width: 260.0,
          primarySectors: 18,
          secondarySectors: 36,
          baseColor: Color.fromRGBO(255, 255, 255, 0.1),
          selectionColor: baseColor,
          handlerColor: Colors.white,
          handlerOutterRadius: 12.0,
          onSelectionChange: _updateLabels,
          sliderStrokeWidth: 12.0,
          child: Padding(
            padding: const EdgeInsets.all(42.0),
            child: Center(
                child: Text('${_formatMovedAngle(initAngle, endAngle)}',
                    style: TextStyle(fontSize: 36.0, color: Colors.white))),
          ),
        ),
        Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
          _formatAnglePosition('START', initAngle),
          _formatAnglePosition('END', endAngle),
        ]),
        FlatButton(
          child: Text('S H U F F L E'),
          color: baseColor,
          textColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(50.0),
          ),
          onPressed: _shuffle,
        ),
      ],
    );
  }

  Widget _formatAnglePosition(String pre, int time) {
    return Column(
      children: [
        Text(pre, style: TextStyle(color: baseColor)),
        Text('ANGLE', style: TextStyle(color: baseColor)),
        Text(
          '${_formatAngle(time)}',
          style: TextStyle(color: Colors.white),
        )
      ],
    );
  }

  String _formatAngle(int angle) {
    if (angle == 0 || angle == null) {
      return '0';
    }
//    var hours = angle ~/ 12;
//    var minutes = (angle % 12) * 5;
    return '${angle * 10} deg';
  }

  String _formatMovedAngle(int init, int end) {
//    var sleepTime = end > init ? end - init : 36 - init + end;
//    var hours = sleepTime ~/ 12;
//    var minutes = (sleepTime % 12) * 5;
    var movedAngle = (end - init).abs() * 10;
    return '${movedAngle} deg';
  }

  Widget _formatRotation(int init, int end) {
    return Column(
      children: <Widget>[
        _formatRotationIcon(init, end),
        Icon(
          Icons.undo,
          color: Colors.white,
          size: 48.0,
        ),
      ],
    );
  }

  Icon _formatRotationIcon(int init, int end) {
    return Icon(
        Icons.redo,
        color: Colors.white,
        size: 48.0,
      );
  }

  int _generateRandomTime() => Random().nextInt(36);
}