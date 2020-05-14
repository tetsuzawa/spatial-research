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
  int startPosition = 0;
  int endPosition = 0;

  void _handlePressRotationButton() {
    setState(() {
      _rotation = !_rotation;
    });
  }

  void _handlePressCircleElementsButton() {
    setState(() {
      //TODO 最初にボタンが押されたらstartをセット
      //TODO 二回目ならendをセット
      //TODO pathを演算する関数を呼び出し
    });
  }

  List<Positioned> createCircleElementsButton(int numElements, double radius) {
    // リストの初期化
    var circleElements = new List<Positioned>();
    // 要素数から角度を計算
    var angle = 360.0 / numElements;
    // ボタンの直径
    var elemRadius = 30.0;

    for (int i = 0; i < numElements; i++) {
      // 角度と座標を計算
      var deg = angle * i;
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
            child: Text(deg.toInt().toString()),
//            child: Text(
//              "b",
//              style: TextStyle(fontSize: 5),
//              textAlign: TextAlign.center,
//            ),

            onPressed: _handlePressCircleElementsButton,
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
                ...createCircleElementsButton(36, circleElementsFieldWidth / 2)
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
