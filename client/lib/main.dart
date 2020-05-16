import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'dart:math' as math;

import 'http_handler.dart';

void main() => runApp(MyApp()); /*1*/

class MyApp extends StatelessWidget {
  /*2*/
  @override
  Widget build(BuildContext context) {
    /*3*/
    return MaterialApp(
      /*4*/
      title: 'Welcome to Flutter',
      theme: new ThemeData.light().copyWith(
        //TODO 色のカスタマイズ
      ),
      home: Scaffold(
        /*5*/
        appBar: AppBar(
          /*6*/
          title: Text('Angle Sender'),
        ),
        body: AngleSender(),
      ),
    );
  }
}

class _AngleSenderState extends State<AngleSender> {
  static final double circleElementsFieldWidth = 800.0;
  static final double circleElementRadius = 30.0;
  static final int numCircleElements = 36;

  ArcPainter _startPainter = ArcPainter(
      Colors.grey[300], circleElementsFieldWidth / 2, circleElementRadius * 2);
  ArcPainter _arcPainter = ArcPainter(Colors.lightBlueAccent[100],
      circleElementsFieldWidth / 2, circleElementRadius * 2);
  ArcPainter _endPainter = ArcPainter(
      Colors.blue, circleElementsFieldWidth / 2, circleElementRadius * 2);

  bool _rotation = false;
  int _startDeg = -1;
  int _endDeg = -1;

  bool _isLoading = true;

  setLoading(bool state) => setState(() => _isLoading = state);
  String _responseMessage = "";

  setResponseMessage(String message) =>
      setState(() => _responseMessage = message);

  void _handlePressRotationButton() {
    SystemSound.play(SystemSoundType.click);
    setState(() {
      _rotation = !_rotation;
      _arcPainter.setArcParams(_startDeg, _endDeg, _rotation);
    });
  }

  void _handlePressClearButton() {
    SystemSound.play(SystemSoundType.click);
    setState(() {
      _rotation = false;
      _startDeg = -1;
      _endDeg = -1;
      _arcPainter.setArcParams(0, 0, _rotation);
      _startPainter.setArcParams(0, 0, _rotation);
      _endPainter.setArcParams(0, 0, _rotation);
    });
    setLoading(true);
  }

  void _handlePressSubmitButton() async {
    SystemSound.play(SystemSoundType.click);
    setResponseMessage("loading...");
    var rotation = _rotation ? "c" : "cc";
    var message = "";
    try {
      setLoading(true);
      message = await postAngle(_startDeg, _endDeg, rotation);
    } finally {
      setLoading(false);
      _handlePressClearButton();
    }
    setResponseMessage(message);
  }

  void _calcInitialRotation() {
    setState(() {
      if (_startDeg < _endDeg) {
        if ((_endDeg - _startDeg).abs() <= (360 - _endDeg + _startDeg).abs()) {
          _rotation = true;
        } else {
          _rotation = false;
        }
      } else {
        if ((_endDeg - _startDeg).abs() <= (360 - _startDeg + _endDeg).abs()) {
          _rotation = false;
        } else {
          _rotation = true;
        }
      }
    });
  }

  void _handlePressCircleElementsButton(int deg) {
    SystemSound.play(SystemSoundType.click);
    setState(() {
      if (_startDeg == -1) {
        // 最初にボタンが押されたらstartをセット
        print("start angle $deg");
        _startDeg = deg;
        this._startPainter.setArcParams(_startDeg - 1, _startDeg + 1, true);
      } else {
        //二回目ならendをセット、pathを計算
        print("end angle $deg");
        setLoading(false);
        _endDeg = deg;
        _calcInitialRotation();
        this._arcPainter.setArcParams(_startDeg, _endDeg, _rotation);
        this._startPainter.setArcParams(_startDeg - 1, _startDeg + 1, true);
        _endPainter.setArcParams(_endDeg - 1, _endDeg + 1, true);
      }
    });
  }

  List<Positioned> _createCircleElements(int numElements, double radius) {
    // リストの初期化
    var circleElements = new List<Positioned>();
    // 要素数から角度を計算
    var angle = 360.0 / numElements;
    // ボタンの半径

    for (int i = 0; i < numElements; i++) {
      // 角度と座標を計算
      var deg = (angle * i).toInt();
      var x = math.cos(deg * math.pi / 180 - math.pi) *
          (radius - circleElementRadius) +
          radius;
      var y = -math.sin(deg * math.pi / 180 - math.pi) *
          (radius - circleElementRadius) +
          radius;
      //リストに子要素を追加
      circleElements.add(
        Positioned(
          top: x - circleElementRadius,
          left: y - circleElementRadius,
          width: circleElementRadius * 2,
          height: circleElementRadius * 2,
          child: FlatButton(
            child: Text(deg.toString()),
            onPressed: () => {_handlePressCircleElementsButton(deg)},
            shape: CircleBorder(),
          ),
        ),
      );
    }
    return circleElements;
  }

  Widget build(BuildContext context) {
    return Center(
      child: Container(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            /* ----------------- Circle Elements -----------------*/
            Stack(
              children: <Widget>[
                Container(
                  width: circleElementsFieldWidth,
                  height: circleElementsFieldWidth,
                  child: Text(_responseMessage),
                  alignment: Alignment.center,
                ),
                CustomPaint(
                  painter: _arcPainter,
                ),
                CustomPaint(
                  painter: _startPainter,
                ),
                CustomPaint(
                  painter: _endPainter,
                ),
                ..._createCircleElements(
                    numCircleElements, circleElementsFieldWidth / 2),
              ],
            ),
            /* ----------------- Circle Elements -----------------*/
            /* ----------------- Buttons -----------------*/
            /* ----------------- Rotation Button -----------------*/
            RaisedButton.icon(
              icon: Icon(
                _rotation ? Icons.autorenew : Icons.sync,
                size: 30.0,
              ),
              label: Text("Rotation"),
              color: Theme
                  .of(context)
                  .primaryColor,
              textColor: Theme
                  .of(context)
                  .primaryTextTheme
                  .bodyText1
                  .color,
              shape: StadiumBorder(),
              onPressed: _handlePressRotationButton,
            ),
            /* ----------------- Rotation Button -----------------*/
            Container(
              child: Center(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: <Widget>[
                    /* ----------------- Clear Button -----------------*/
                    RaisedButton.icon(
                      icon: Icon(
                        Icons.clear,
                        size: 30.0,
                      ),
                      label: Text("Clear"),
                      color: Colors.grey[400],
                      textColor:
                      Theme
                          .of(context)
                          .primaryTextTheme
                          .bodyText1
                          .color,
                      shape: StadiumBorder(),
                      onPressed: _handlePressClearButton,
                    ),
                    /* ----------------- Clear Button -----------------*/
                    /* ----------------- Submit Button -----------------*/
                    RaisedButton.icon(
                      icon: Icon(
                        Icons.send,
                        size: 30.0,
                      ),
                      label: Text("Submit"),
                      color: Theme
                          .of(context)
                          .accentColor,
                      textColor:
                      Theme
                          .of(context)
                          .primaryTextTheme
                          .bodyText1
                          .color,
                      shape: StadiumBorder(),
                      onPressed: _isLoading ? null : _handlePressSubmitButton,
                    ),
                    /* ----------------- Submit Button -----------------*/
                  ],
                ),
              ),
            ),
            /* ----------------- Buttons -----------------*/
          ],
        ),
      ),
    );
  }
}

class AngleSender extends StatefulWidget {
  @override
  _AngleSenderState createState() => _AngleSenderState();
}

class ArcPainter extends CustomPainter {
  int startDeg = 0;
  int endDeg = 0;
  bool rotation = false;
  Color color;
  double rectRadius;
  double strokeWidth;

  @override
  ArcPainter(this.color, this.rectRadius, this.strokeWidth);

  setArcParams(int startDeg, int endDeg, bool rotation) {
    this.startDeg = startDeg;
    this.endDeg = endDeg;
    this.rotation = rotation;
  }

  static double deg2rad(double deg) {
    return deg * math.pi / 180;
  }

  @override
  void paint(Canvas canvas, Size size) {
    Offset offsetCenter = Offset(rectRadius, rectRadius);
    final Rect rect = Rect.fromCircle(
        center: offsetCenter, radius: rectRadius - strokeWidth / 2);
    final double offSetRad = math.pi / 2;
    double startRad = startDeg * math.pi / 180 - offSetRad;
    double sweepRad;
    if (startDeg < endDeg) {
      if (rotation) {
        sweepRad = deg2rad((endDeg - startDeg).toDouble());
      } else {
        sweepRad = deg2rad(-(360.0 - endDeg + startDeg));
      }
    } else {
      if (rotation) {
        sweepRad = deg2rad(360.0 - startDeg + endDeg);
      } else {
        sweepRad = deg2rad((endDeg - startDeg).toDouble());
      }
    }
    final useCenter = false;
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..isAntiAlias = true
      ..strokeCap = StrokeCap.round
      ..strokeWidth = strokeWidth;

    canvas.drawArc(rect, startRad, sweepRad, useCenter, paint);
  }

  @override
  bool shouldRepaint(CustomPainter old) {
    return false;
  }
}
