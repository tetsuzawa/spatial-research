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
  bool _rotation = true;
  int startDeg = -1;
  int endDeg = -1;

  void _handlePressRotationButton() {
    setState(() {
      _rotation = !_rotation;
    });
  }

  void _handlePressCircleElementsButton(int deg) {
    print("pressed $deg");
    setState(() {
      if (this.startDeg == -1) {
        // 最初にボタンが押されたらstartをセット
        print("start angle $deg");
        this.startDeg = deg;
      } else {
        //二回目ならendをセット、pathを計算
        print("end angle $deg");
        this.startDeg = deg;
        // TODO
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
                  painter: ArcPainter(),
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
  double startDeg = 30.0;
  double endDeg = 260.0;
  bool rotation = false;

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
    final paint = Paint()
      ..color = Colors.lightBlueAccent[100]
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
