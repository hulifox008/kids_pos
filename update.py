#!/usr/bin/env python

import os
import sys
import random
import sqlite3
from PySide6 import QtCore, QtWidgets, QtGui
from PIL import Image
from PIL.ImageQt import ImageQt

MAX_BARCODE_LEN=40
UPLOAD_FILE='/tmp/upload.jpg'

class MerchandiseStorage():
    def __init__(self):
        self.conn = sqlite3.connect('pos.db')

    def save(self, info):
        self.conn.execute("INSERT INTO merchandise(barcode, desc, price) VALUES(?, ?, ?) ON CONFLICT(barcode) DO UPDATE SET desc=excluded.desc,price=excluded.price", (info['barcode'], info['name'], info['price'])) 
        self.conn.commit()

    def load(self, barcode):
        cur = self.conn.cursor()
        row = cur.execute('SELECT desc,price from merchandise WHERE barcode=?', (barcode,)).fetchone()
        return row


def process_uploaded_image():
    img = Image.open(UPLOAD_FILE)
    w,h = img.size
    if w>h:
        img = img.crop( ((w-h)/2, 0, (w-h)/2+h, h)).resize((300,300))
    elif h>w:
        img = img.crop( (0, (h-w)/2, w, (h-w)/2+w)).resize((300,300))

    img = img.resize((300,300))
    return img



class IDLineEdit(QtWidgets.QLineEdit):
    def focusInEvent(self, e):
        super(IDLineEdit, self).focusInEvent(e)
        QtCore.QTimer.singleShot(0, self.selectAll)

class MyWidget(QtWidgets.QWidget):
    def __init__(self, pipe_r):
        super().__init__()

        self.img_dir = os.path.dirname(sys.argv[0]) + '/static/img/'

        self.storage = MerchandiseStorage()
        self.pipe_r = pipe_r
        self.uploaded_img = None

        self.label_id = QtWidgets.QLabel("编号:");
        self.edit_id = IDLineEdit();
        self.edit_id.returnPressed.connect(self.barcode_ready)

        self.label_name = QtWidgets.QLabel("名称:");
        self.edit_name = QtWidgets.QLineEdit();

        self.label_price = QtWidgets.QLabel("价格($):");
        self.edit_price = QtWidgets.QLineEdit();
        input_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("[0-9]+.?[0-9]+{,2}"))
        self.edit_price.setValidator(input_validator)

        self.label_image = QtWidgets.QLabel();
        self.label_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_image.setFixedSize(300, 300);

        self.formlayout = QtWidgets.QFormLayout(self)
        self.formlayout.setVerticalSpacing(30)
        self.formlayout.addRow(self.label_id, self.edit_id)
        self.formlayout.addRow(self.label_name, self.edit_name)
        self.formlayout.addRow(self.label_price, self.edit_price)
        self.formlayout.addRow(self.label_image)

        self.ok_btn = QtWidgets.QPushButton("更新");
        self.ok_btn.setFixedSize(80, 50)
        self.ok_btn.clicked.connect(self.button_clicked)
        self.formlayout.addRow(self.ok_btn);


    @QtCore.Slot()
    def button_clicked(self, arg1):
        self.storage.save({'barcode':self.edit_id.text(), 'name':self.edit_name.text(), 'price':self.edit_price.text()})
        img_name = self.edit_id.text().strip()
        if self.uploaded_img and len(img_name) > 0 and len(img_name)<= MAX_BARCODE_LEN:
            self.uploaded_img.save(self.img_dir + img_name + '.jpg')
            
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Success!");
        dlg.setText("Success");
        dlg.exec()

    @QtCore.Slot()
    def barcode_ready(self):
        barcode = self.edit_id.text().strip()
        self.label_image.setPixmap(QtGui.QPixmap(self.img_dir + '/' + barcode + '.jpg'))
        rec = self.storage.load(barcode)
        if rec:
            self.edit_name.setText(rec[0])
            self.edit_price.setText(str(rec[1]))
        else:
            self.edit_name.setText('')
            self.edit_price.setText('')

        self.edit_id.selectAll()
        

    @QtCore.Slot()
    def image_ready(self, arg1):
        if(len(os.read(self.pipe_r, 1))!=1):
            # the pipe has been closed due to child process terminated
            exit(1)
        print("image ready")
        self.uploaded_img = process_uploaded_image()
        self.label_image.setPixmap(QtGui.QPixmap.fromImage(ImageQt(self.uploaded_img)))

if __name__ == "__main__":
    pipe_r, pipe_w = os.pipe()

    processid = os.fork()
    if processid:
        #In parent
        from flask import Flask, request, send_file
        app = Flask(__name__)

        os.close(pipe_r)
        
        @app.route("/")
        def hello_world():
            return send_file('index.html')
        
        @app.route('/image_upload', methods=['POST'])
        def barcode_decode():
            if request.method == "POST":
                fs = request.files['file']
                print(fs.content_length)
                fs.save(UPLOAD_FILE)
                os.write(pipe_w, b'+')
                return {'status':'OK'}
        
        app.run(host='0.0.0.0')
        exit(0)


    os.close(pipe_w)

    app = QtWidgets.QApplication([])
    app.setStyleSheet("QLabel{font-size:18pt;} QLineEdit{font-size:18pt;}")
    app.setStyleSheet("*{font-size:18pt;}")

    widget = MyWidget(pipe_r)
    widget.resize(800, 600)
    widget.show()

    notifier = QtCore.QSocketNotifier(pipe_r, QtCore.QSocketNotifier.Read,  widget)
    notifier.setEnabled(True)

    QtCore.QObject.connect(notifier, QtCore.SIGNAL("activated(int)"), widget.image_ready)

    sys.exit(app.exec())
