import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'http_handler.dart';

class _SettingsState extends State<Settings> {
  TextEditingController _textEditingController;
  String _responseMessage = "";
  bool _isLoading = false;

  setLoading(bool state) => setState(() => _isLoading = state);

  _setResponseMessage(String message) =>
      setState(() => _responseMessage = message);

  void _handlePressPingButton() async {
    SystemSound.play(SystemSoundType.click);
    _setResponseMessage("loading...");
    var message = "";
    try {
      setLoading(true);
      message = await getPing();
    } finally {
      setLoading(false);
    }
    _setResponseMessage(message);
  }

  @override
  void initState() {
    super.initState();
    _textEditingController = TextEditingController(text: API_BASE_URL);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        /*6*/
        title: Text('Settings'),
      ),
      body: Center(
        child: Container(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: <Widget>[
              Container(
                child: TextField(
                  controller: _textEditingController,
                  decoration: InputDecoration(
                    labelText: "URL",
                    hintText: "http://172.24.176.10:8888",
                  ),
                  onChanged: (String url) => {API_BASE_URL = url},
                ),
                width: MediaQuery.of(context).size.width * 0.6,
              ),
              RaisedButton(
                child: Text("Ping"),
                color: Theme.of(context).primaryColor,
                textColor: Theme.of(context).primaryTextTheme.bodyText1.color,
                shape: StadiumBorder(),
                onPressed: _isLoading ? null : _handlePressPingButton,
              ),
              Text(_responseMessage),
            ],
          ),
        ),
      ),
    );
  }
}

class Settings extends StatefulWidget {
  @override
  _SettingsState createState() => _SettingsState();
}
