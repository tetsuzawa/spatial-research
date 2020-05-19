import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  static const String _title = 'Flutter Code Sample';

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: _title,
      home: Scaffold(
        appBar: AppBar(title: Text(_title)),
        body: ImageWidget(),
      ),
    );
  }
}

class ImageWidget extends StatelessWidget {
  ImageWidget({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
//        child: AspectRatio(
//          aspectRatio: 1 / 1,
          child: Container(
            color: Colors.blue,
            child: Text(MediaQuery.of(context).size.width.toString()),
            alignment: Alignment.center,

          ),
//        ),
        width: MediaQuery.of(context).size.width * 0.8,
        height: MediaQuery.of(context).size.width * 0.8,
      ),
    );
  }
}
