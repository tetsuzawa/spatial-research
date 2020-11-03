import time
import random, string

from flask import Flask, jsonify, request


def randomname(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)


app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Hello World!'})


@app.route('/', methods=['POST'])
def angle_reciever():
    time.sleep(1)  # 何らかの処理
    json = request.get_json()
    print("start degree:", json['start_degree'])
    print("end degree:", json['end_degree'])
    print("rotation:", json['rotation'])
    return jsonify({'message': 'OK'})


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'OK'})


@app.route('/words')
def random_words():
    time.sleep(1)
    return jsonify({'message': randomname(5)})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)
