import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt

class MyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("基于Python的UI设计")
        self.setGeometry(300, 300, 800, 600)

        # 创建标签和按钮
        self.label = QLabel(self)
        self.label.setGeometry(50, 50, 400, 400)

        self.button = QPushButton("选择图片", self)
        self.button.setGeometry(200, 470, 100, 30)
        self.button.clicked.connect(self.showDialog)

        self.compare_label = QLabel(self)
        self.compare_label.setGeometry(460, 50, 300, 300)

        self.reconstruct_button = QPushButton("重建人脸", self)
        self.reconstruct_button.setGeometry(550, 470, 100, 30)
        self.reconstruct_button.clicked.connect(self.reconstructFace)

        # 初始化变量
        self.img_path = None
        self.img = None
        self.rect = None

    def showDialog(self):
        # 弹出文件选择对话框
        fname = QFileDialog.getOpenFileName(self, '选择图片', '.', 'Image files(*.jpg *.gif *.png)')[0]
        if fname:
            # 显示选择的图片
            self.img_path = fname
            pixmap = QPixmap(fname)
            self.label.setPixmap(pixmap.scaled(self.label.width(), self.label.height()))
            self.label.mousePressEvent = self.getPos

    def getPos(self, event):
        # 获取鼠标点击位置
        x = event.pos().x()
        y = event.pos().y()
        w = 100
        h = 100
        self.rect = (x, y, w, h)
        self.drawRect()

    def drawRect(self):
        # 绘制矩形框
        img = cv2.imread(self.img_path)
        x, y, w, h = self.rect
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        bytesPerLine = c*w
        qImg = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.label.setPixmap(pixmap.scaled(self.label.width(), self.label.height()))

    def reconstructFace(self):
        if self.img_path and self.rect:
            # 超分辨重建人脸
            img = cv2.imread(self.img_path)
            x, y, w, h = self.rect
            face = img[y:y+h, x:x+w]
            face = cv2.resize(face, (int(w*4), int(h*4)), interpolation=cv2.INTER_CUBIC)
            face = cv2.resize(face, (w, h), interpolation=cv2.INTER_CUBIC)

            # 显示低分辨图像和重建图像的对比图
            img_low = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_high = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            h, w, c = img_low.shape
            bytesPerLine = c*w
            qImg_low = QImage(img_low.data, w, h, bytesPerLine, QImage.Format_RGB888)
            qImg_high = QImage(img_high.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap_low = QPixmap.fromImage(qImg_low)
            pixmap_high = QPixmap.fromImage(qImg_high)
            self.label.setPixmap(pixmap_low.scaled(self.label.width(), self.label.height()))
            self.compare_label.setPixmap(pixmap_high.scaled(self.compare_label.width(), self.compare_label.height()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myui = MyUI()
    myui.show()
    sys.exit(app.exec_())