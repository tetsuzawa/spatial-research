import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'dart:math' as math;

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
  ArcPainter arcPainter = ArcPainter(Colors.lightBlueAccent[100]);
  ArcPainter startPainter = ArcPainter(Colors.grey[300]);
  ArcPainter endPainter = ArcPainter(Colors.blue);

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

  void _handlePressSubmitButton() {
    //TODO
  }

  void _calcInitialRotation() {
    print("called");
    if ((this.endDeg - this.startDeg).abs() <=
        (360 - this.endDeg + this.startDeg).abs()) {
      this._rotation = true;
    } else {
      this._rotation = false;
    }
  }

  void _handlePressCircleElementsButton(int deg) {
    print("pressed $deg");
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
        // TODO
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

  List<Positioned> createCircleElementsButton(int numElements, double radius) {
    // リストの初期化
    var circleElements = new List<Positioned>();
    // 要素数から角度を計算
    var angle = 360.0 / numElements;
    // ボタンの直径
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
            key: Key("angle-${deg.toString()}"),
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
                  child: Text('word'),
                  alignment: Alignment.center,
                ),
                CustomPaint(
//                  size: Size(circleElementsFieldWidth / 2,
//                      circleElementsFieldWidth / 2),
                  painter: arcPainter,
                ),
                CustomPaint(
                  painter: startPainter,
                ),
                CustomPaint(
                  painter: endPainter,
                ),
                ...createCircleElementsButton(36, circleElementsFieldWidth / 2),
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
                      onPressed: _handlePressSubmitButton,
                    ),
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
    final rect = Rect.fromLTRB(30, 30, 770, 770);
    double startRad = startDeg * math.pi / 180 - math.pi / 2;
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
    // a fancy rainbow gradient
    final Gradient gradient = new SweepGradient(
      endAngle: endDeg / math.pi/180- math.pi / 2
      colors: [
        Colors.white,
        currentDotColor,
      ],
    );
    final paint = Paint()
      ..color = this.color
      ..style = PaintingStyle.stroke
      ..isAntiAlias = true
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 60
      ..shader = gradient.createShader();

    canvas.drawArc(rect, startRad, sweepRad, useCenter, paint);
  }

  @override
  bool shouldRepaint(CustomPainter old) {
    return false;
  }
}

/*

class _RotationButtonState extends State<RotationButton> {
  bool rotation = true;

  void _handlePress() {
    setState(() {
      rotation = !rotation;
    });
  }

  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _handlePress,
      child: Center(
        child: RaisedButton.icon(
          icon: Icon(
            rotation ? Icons.autorenew : Icons.sync,
            size: 30.0,
            color: Theme.of(context).backgroundColor,
          ),
          label: Text("Rotation"),
          color: Theme.of(context).primaryColor,
          textColor: Theme.of(context).backgroundColor,
          shape: StadiumBorder(),
          onPressed: _handlePress,
        ),
      ),
    );
  }
}

class RotationButton extends StatefulWidget {
  @override
  _RotationButtonState createState() => _RotationButtonState();
}
*/

/*
class RandomWordsState extends State<RandomWords> {
  @override
  Widget build(BuildContext context) {
    final wordPair = WordPair.random();
    return Text(wordPair.asPascalCase);
  }
}

class RandomWords extends StatefulWidget {
  @override
  RandomWordsState createState() => new RandomWordsState();

}
 */
