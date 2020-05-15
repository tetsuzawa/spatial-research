import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

///*
Future<String> fetchMessageResponse() async {
  final response = await http.get('http://localhost:8888/words');

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    var messageResponse = MessageResponse.fromJson(json.decode(response.body));
    return messageResponse.message;
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load album');
  }
}
//*/

class MessageResponse {
  final String message;

  MessageResponse({this.message});

  factory MessageResponse.fromJson(Map<String, dynamic> json) {
    return MessageResponse(
      message: json['message'],
    );
  }
}
