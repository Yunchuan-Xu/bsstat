# -*- coding: utf-8 -*-
import os
import json
from logging.config import dictConfig

from flask import Flask, jsonify, Response


__author__ = 'Yunchuan Xu'


with open('logging_conf.json') as config_file:
    config_dict = json.load(config_file)
dictConfig(config_dict)

app = Flask(__name__)


@app.route('/health')
def health():
    response = {'status': 'UP'}
    return jsonify(response)


@app.route('/get_image/<image_name>')
def get_image(image_name):
    if not os.path.exists(image_name):
        return jsonify('image not found')
    else:
        with open(image_name, 'rb') as f:
            image = f.read()
    return Response(image, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
