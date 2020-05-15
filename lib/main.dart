import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'dart:async';
import 'dart:convert';
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
          title: Text('Welcome to Flutter'),
        ),
        body: AngleSender(),
      ),
    );
  }
}

class _AngleSenderState extends State<AngleSender> {
  bool _rotation = false;
  int startDeg = -1;
  int endDeg = -1;
  ArcPainter startPainter = ArcPainter(Colors.grey[300]);
  ArcPainter arcPainter = ArcPainter(Colors.lightBlueAccent[100]);
  ArcPainter endPainter = ArcPainter(Colors.blue);

  bool isLoading = false;

  setLoading(bool state) => setState(() => isLoading = state);
  String _responseMessage = "";
  setResponseMessage(String message) => setState(() => _responseMessage = message);

  _AngleSenderState();

  void _handlePressRotationButton() {
    setState(() {
      _rotation = !_rotation;
      this.arcPainter.setArcParams(this.startDeg, this.endDeg, this._rotation);
    });
  }

  void _handlePressClearButton() {
    setState(() {
      _rotation = false;
      this.startDeg = -1;
      this.endDeg = -1;
      this.arcPainter.setArcParams(0, 0, this._rotation);
      this.startPainter.setArcParams(0, 0, this._rotation);
      this.endPainter.setArcParams(0, 0, this._rotation);
    });
  }

  void _handlePressSubmitButton() async {
    setResponseMessage("loading...");
    var message = "";
    try {
      setLoading(true);
      message = await fetchMessageResponse();
    } finally {
      setLoading(false);
      _handlePressClearButton();
    }
    setResponseMessage(message);
  }

  void _calcInitialRotation() {
    setState(() {
      if (startDeg < endDeg) {
        if ((this.endDeg - this.startDeg).abs() <=
            (360 - this.endDeg + this.startDeg).abs()) {
          this._rotation = true;
        } else {
          this._rotation = false;
        }
      } else {
        if ((this.endDeg - this.startDeg).abs() <=
            (360 - this.startDeg + this.endDeg).abs()) {
          this._rotation = false;
        } else {
          this._rotation = true;
        }
      }
    });
  }

  void _handlePressCircleElementsButton(int deg) {
    setState(() {
      if (this.startDeg == -1) {
        // 最初にボタンが押されたらstartをセット
        print("start angle $deg");
        this.startDeg = deg;
        this
            .startPainter
            .setArcParams(this.startDeg - 1, this.startDeg + 1, true);
      } else {
        //二回目ならendをセット、pathを計算
        print("end angle $deg");
        this.endDeg = deg;
        _calcInitialRotation();
        this
            .arcPainter
            .setArcParams(this.startDeg, this.endDeg, this._rotation);
        this
            .startPainter
            .setArcParams(this.startDeg - 1, this.startDeg + 1, true);
        this.endPainter.setArcParams(this.endDeg - 1, this.endDeg + 1, true);
      }
    });
  }

  List<Positioned> _createCircleElements(int numElements, double radius) {
    // リストの初期化
    var circleElements = new List<Positioned>();
    // 要素数から角度を計算
    var angle = 360.0 / numElements;
    // ボタンの半径
    const elemRadius = 30.0;

    for (int i = 0; i < numElements; i++) {
      // 角度と座標を計算
      var deg = (angle * i).toInt();
      var x = math.cos(deg * math.pi / 180 - math.pi) * (radius - elemRadius) +
          radius;
      var y = -math.sin(deg * math.pi / 180 - math.pi) * (radius - elemRadius) +
          radius;

      circleElements.add(
        Positioned(
          top: x - elemRadius,
          left: y - elemRadius,
          width: elemRadius * 2,
          height: elemRadius * 2,
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
    const circleElementsFieldWidth = 800.0;
    return Center(
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            /* ----------------- Circle Elements -----------------*/
            Stack(
              children: <Widget>[
                Container(
                  width: circleElementsFieldWidth,
                  height: circleElementsFieldWidth,
//                  child: FutureBuilder<MessageResponse>(
//                    future: futureMessageResponse,
//                    builder: (context, snapshot) {
//                      if (snapshot.hasData) {
//                        return Text(snapshot.data.message);
//                      } else if (snapshot.hasError) {
//                        return Text("${snapshot.error}");
//                      }
//                      // By default, show a loading spinner.
//                      return CircularProgressIndicator();
//                    },
//                  ),
                  child: Text(_responseMessage),
                  alignment: Alignment.center,
                ),
                CustomPaint(
                  painter: arcPainter,
                ),
                CustomPaint(
                  painter: startPainter,
                ),
                CustomPaint(
                  painter: endPainter,
                ),
                ..._createCircleElements(36, circleElementsFieldWidth / 2),
              ],
            ),
            /* ----------------- Circle Elements -----------------*/
            /* ----------------- Rotation Button -----------------*/
            RaisedButton.icon(
              icon: Icon(
                _rotation ? Icons.autorenew : Icons.sync,
                size: 30.0,
              ),
              label: Text("Rotation"),
              color: Theme.of(context).primaryColor,
              textColor: Theme.of(context).primaryTextTheme.bodyText1.color,
              shape: StadiumBorder(),
              onPressed: _handlePressRotationButton,
            ),
            /* ----------------- Rotation Button -----------------*/
            /* ----------------- Buttons -----------------*/
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
                          Theme.of(context).primaryTextTheme.bodyText1.color,
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
                      color: Theme.of(context).accentColor,
                      textColor:
                          Theme.of(context).primaryTextTheme.bodyText1.color,
                      shape: StadiumBorder(),
                      onPressed: isLoading ? null : _handlePressSubmitButton,
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

  @override
  ArcPainter(this.color);

  setArcParams(int startDeg, int endDeg, bool rotation) {
    this.startDeg = startDeg;
    this.endDeg = endDeg;
    this.rotation = rotation;
  }

  //         <-- CustomPainter class
  @override
  void paint(Canvas canvas, Size size) {
    Offset offsetCenter = Offset(400, 400);
    final Rect rect = Rect.fromCircle(center: offsetCenter, radius: 370);
    final double offSetRad = math.pi / 2;
    double startRad = startDeg * math.pi / 180 - offSetRad;
    double sweepRad;
    if (startDeg < endDeg) {
      if (rotation) {
        sweepRad = (endDeg - startDeg) * math.pi / 180;
      } else {
        sweepRad = -(360 - endDeg + startDeg) * math.pi / 180;
      }
    } else {
      if (rotation) {
        sweepRad = (360 - startDeg + endDeg) * math.pi / 180;
      } else {
        sweepRad = (endDeg - startDeg) * math.pi / 180;
      }
    }
    final useCenter = false;
    final Gradient gradient = new SweepGradient(
      endAngle: endDeg * math.pi / 180 - offSetRad,
      colors: [
        Colors.white,
        this.color,
      ],
    );
    final paint = Paint()
      ..color = this.color
      ..style = PaintingStyle.stroke
      ..isAntiAlias = true
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 60;

    canvas.drawArc(rect, startRad, sweepRad, useCenter, paint);
  }

  @override
  bool shouldRepaint(CustomPainter old) {
    return false;
  }
}
