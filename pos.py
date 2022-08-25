#!/usr/bin/env python

import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("付款")
        self.button.setFixedSize(200,150)
        font = self.button.font()
        font.setPointSize(48)
        self.button.setFont(font)

        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)
        self.text.setFont(font)


        self.glayout = QtWidgets.QGridLayout(self)
        self.glayout.addWidget(self.text, 0, 0, QtCore.Qt.AlignCenter)        
        self.glayout.setRowStretch(0, 80)
        self.glayout.setRowStretch(1, 20)
        self.glayout.addWidget(self.button, 1, 1, QtCore.Qt.AlignCenter)
        self.glayout.setColumnStretch(0, 80)
        self.glayout.setColumnStretch(1, 20)

        self.label_total = QtWidgets.QLabel("Total:")
        self.label_total.setFont(font)
        self.glayout.addWidget(self.label_total, 1, 0)


        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))
        self.label_total.setText("Total: $100.0")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
