from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
import sys
import os
import cv2
import pyautogui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie


# from image_ai import analyze_image


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class Avatar(QWidget):
    def __init__(self):
        super().__init__()

        # self.gallery_btn.clicked.connect(self.open_gallery)
        # self.camera_btn.clicked.connect(self.open_camera)
        # self.screen_btn.clicked.connect(self.take_screenshot)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(600, 300)

        self.old_pos = None  # ✅ Fix drag crash
        # Avatar GIF
        self.avatar_label = QLabel(self)
        self.avatar_label.setGeometry(0, 50, 200, 200)

        self.idle_movie = QMovie(resource_path("assets/idle.gif"))
        self.thinking_movie = QMovie(resource_path("assets/thinking.gif"))

        self.avatar_label.setMovie(self.idle_movie)
        self.idle_movie.start()

        # Text bubble
        self.text_label = QLabel(self)
        self.text_label.setGeometry(220, 20, 350, 200)
        #self.text_label.setGeometry(330, 20, 250, 200)
        self.text_label.setWordWrap(True)

        self.text_label.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 12px;
            font-size: 14px;
            color: black;
        """)

        self.text_label.setText("Hi handsome 😌")

        # # -------- LEFT BUTTONS --------
        # self.gallery_btn = QPushButton("📂", self)
        # self.gallery_btn.setGeometry(20, 60, 60, 40)
        #
        # self.camera_btn = QPushButton("📷", self)
        # self.camera_btn.setGeometry(20, 110, 60, 40)
        #
        # self.screen_btn = QPushButton("🖥", self)
        # self.screen_btn.setGeometry(20, 160, 60, 40)
        #
        # # Style
        # button_style = """
        #     QPushButton {
        #         background-color: white;
        #         border-radius: 10px;
        #         font-size: 18px;
        #     }
        #     QPushButton:hover {
        #         background-color: lightgray;
        #     }
        # """
        #
        # self.gallery_btn.setStyleSheet(button_style)
        # self.camera_btn.setStyleSheet(button_style)
        # self.screen_btn.setStyleSheet(button_style)
        #
        # # ✅ CONNECT AFTER CREATION
        # self.gallery_btn.clicked.connect(self.open_gallery)
        # self.camera_btn.clicked.connect(self.open_camera)
        # self.screen_btn.clicked.connect(self.take_screenshot)

    def set_thinking(self):
        self.idle_movie.stop()
        self.avatar_label.setMovie(self.thinking_movie)
        self.thinking_movie.start()
        self.text_label.setText("Thinking...")

    def set_idle(self):
        self.thinking_movie.stop()
        self.avatar_label.setMovie(self.idle_movie)
        self.idle_movie.start()

    def speak_text(self, text):
        self.text_label.setText(text)
        self.text_label.adjustSize()

        if self.text_label.width() > 300:
            self.text_label.setFixedWidth(300)
            self.text_label.adjustSize()

    def open_gallery(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.process_image(file_path)

    def open_camera(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            file_path = "camera_capture.jpg"
            cv2.imwrite(file_path, frame)
            self.process_image(file_path)
        cap.release()

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        file_path = "screenshot.png"
        screenshot.save(file_path)
        self.process_image(file_path)

    def process_image(self, path):
        self.set_thinking()

        result = analyze_image(path)

        self.speak_text(result)

        self.set_idle()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
