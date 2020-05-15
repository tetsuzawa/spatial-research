import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

Future<MessageResponse> fetchMessageResponse() async {
  final response =
//      await http.get('https://jsonplaceholder.typicode.com/albums/1');
      await http.get('http://localhost:8888/words');

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    return MessageResponse.fromJson(json.decode(response.body));
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load album');
  }
}

class MessageResponse {
  final String message;

  MessageResponse({this.message});

  factory MessageResponse.fromJson(Map<String, dynamic> json) {
    return MessageResponse(
      message: json['message'],
    );
  }
}

void main() => runApp(MyApp());

class MyApp extends StatefulWidget {
  MyApp({Key key}) : super(key: key);

  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  Future<MessageResponse> futureMessageResponse;

//  @override
//  void initState() {
//    super.initState();
//    futureMessageResponse = fetchMessageResponse();
//  }

  void _handlePressButton() async {
    print("called: _handlePressButton");
    setState(() {
      futureMessageResponse = fetchMessageResponse();
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fetch Data Example',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: Scaffold(
        appBar: AppBar(
          title: Text('Fetch Data Example'),
        ),
        body: Container(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: <Widget>[
//                FutureBuilder<MessageResponse>(
//                  future: futureMessageResponse,
//                  builder: (context, snapshot) {
//                    if (snapshot.hasData) {
//                      return Text(snapshot.data.message);
//                    } else if (snapshot.hasError) {
//                      return Text("${snapshot.error}");
//                    }
//                    // By default, show a loading spinner.
//                    return CircularProgressIndicator();
//                  },
//                ),
                FlatButton(
                  child: Text("do request"),
                  onPressed: () => {_handlePressButton()},
                  shape: CircleBorder(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
