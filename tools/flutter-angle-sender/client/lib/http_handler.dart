import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

const API_BASE_URL = 'http://192.168.1.89:8888';

/* ----------------------- Response -----------------------*/
class Response {
  final String message;

  Response({this.message});

  factory Response.fromJson(Map<String, dynamic> json) {
    return Response(
      message: json['message'],
    );
  }
}
/* ----------------------- Response -----------------------*/

/* ----------------------- Request -----------------------*/
class Request {
  final int startDegree;
  final int endDegree;
  final String rotation;

  Request(this.startDegree, this.endDegree, this.rotation);

  Map<String, dynamic> toJson() => {
        'start_degree': startDegree,
        'end_degree': endDegree,
        'rotation': rotation,
      };
}
/* ----------------------- Request -----------------------*/

/* ----------------------- ping用 (HTTP GET) -----------------------*/
Future<String> getPingMessage() async {
  final endPoint = API_BASE_URL + '/ping';
  http.Response response;
  try {
    response = await http.get(endPoint).timeout(Duration(seconds: 10));
  } on TimeoutException catch (e) {
    return "Error: submission timeout";
  } on Error catch (e) {
    throw e;
  }

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    var messageResponse = Response.fromJson(json.decode(response.body));
    return messageResponse.message;
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load ping');
  }
}
/* ----------------------- ping用 (HTTP GET) -----------------------*/

/* ----------------------- 角度送信用 (HTTP POST) -----------------------*/
Future<String> postAngle(int startDeg, int endDeg, String rotation) async {
  final endPoint = API_BASE_URL + '/';
  var request = new Request(startDeg, endDeg, rotation);
  http.Response response;
  try {
    response = await http.post(endPoint,
        body: json.encode(request.toJson()),
        headers: {
          "Content-Type": "application/json"
        }).timeout(Duration(seconds: 10));
  } on TimeoutException catch (e) {
    return "Timeout";
  } on Error catch (e) {
    throw e;
  }

  if (response.statusCode == 200) {
    // If server returns an OK response, parse the JSON
    var messageResponse = Response.fromJson(json.decode(response.body));
    return messageResponse.message;
  } else {
    // If that response was not OK, throw an error.
    throw Exception('Failed to load post');
  }
}
/* ----------------------- 角度送信用 (HTTP POST) -----------------------*/
