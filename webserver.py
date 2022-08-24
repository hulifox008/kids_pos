#!/usr/bin/env python

from PIL import Image
from flask import Flask, request, send_file
from pyzbar.pyzbar import decode

app = Flask(__name__)

@app.route("/")
def hello_world():
    return send_file('index.html')

@app.route("/barcode_decode", methods=['POST'])
def barcode_decode():
    if request.method == "POST":
        fs = request.files['file']
        print(fs.content_length)
        fs.save('/tmp/upload.jpg')
        print(decode(Image.open('/tmp/upload.jpg')))
        return {'status':'OK'}

app.run(host='0.0.0.0')
