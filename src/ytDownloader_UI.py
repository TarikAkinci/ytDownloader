from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPropertyAnimation
import shutil
import sys
from PySide6.QtWidgets import *
from pytubefix import YouTube
import instaloader
import subprocess
import os
import ssl
import certifi
import re

class Downloader:
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

    def download_video(vid_url, path):
        yt = YouTube(vid_url)
        vid_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, res='720p').first()
        audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

        if vid_stream is None:
            vid_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        vid_stream.download(output_path=path, filename='video.mp4')
        audio_stream.download(output_path=path, filename='audio.mp4')

        return yt.title

    def download_audio(vid_url, path):
        yt = YouTube(vid_url)
        audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
        audio_stream.download(output_path=path, filename=yt.title + '.mp3')

    def remux_streams(path, output_filename):
        video_path = os.path.join(path, 'video.mp4')
        audio_path = os.path.join(path, 'audio.mp4')
        output_path = os.path.join(path, output_filename)

        command = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',
            output_path
        ]

        subprocess.run(command, check=True)
        os.remove(video_path)
        os.remove(audio_path)
        print(f'Remuxing complete: {output_path}')

    def instagram_downloader(url, path):
        loader = instaloader.Instaloader(
            download_comments=False,
            download_geotags=False,
            download_pictures=False,
            download_video_thumbnails=False,
            save_metadata=False
        )

        # replace with any valid post link/url
        shortcode = url.split('/')[-2]

        try:
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            # target is the folder name where it's going to be saved
            # you can call it anything you like
            os.chdir(path)

            title = post.title if post.title else shortcode
            safe_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', title).strip()
            if not safe_title:
                safe_title = shortcode

            loader.download_post(post, target=safe_title)

            folder_path = path + safe_title
            for filename in os.listdir(folder_path):
                if filename.lower().endswith('.mp4'):
                    src_file = os.path.join(folder_path, filename)
                    dst_file = os.path.join("./", filename)
                    shutil.move(src_file, dst_file)

            shutil.rmtree(folder_path)

        except Exception as e:
            print(f'Something went wrong: {e}')

class HoverButton(QtWidgets.QPushButton):
        def __init__(self, label, *args, **kwargs):
                super(HoverButton, self).__init__(*args, **kwargs)
                self.label = label
                self.original_geometry = self.label.geometry()
                self.setMouseTracking(True)
                self.label.setMouseTracking(True)

        def enterEvent(self, event):
                animation = QPropertyAnimation(self.label, b"geometry")
                animation.setDuration(200)
                animation.setStartValue(self.label.geometry())
                enlarged_rect = self.label.geometry().adjusted(-10, -10, 10, 10)
                animation.setEndValue(enlarged_rect)
                animation.start()
                self.animation = animation
                super(HoverButton, self).enterEvent(event)

        def leaveEvent(self, event):
                animation = QPropertyAnimation(self.label, b"geometry")
                animation.setDuration(200)
                animation.setStartValue(self.label.geometry())
                animation.setEndValue(self.original_geometry)
                animation.start()
                self.animation = animation
                super(HoverButton, self).leaveEvent(event)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.url = ""
        self.path = "C:/Users/atari/Downloads"
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(726, 465)
        MainWindow.setStyleSheet("background-color: rgb(18, 18, 18);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.yt_icon = QtWidgets.QLabel(self.centralwidget)
        self.yt_icon.setGeometry(QtCore.QRect(60, 120, 281, 191))
        self.yt_icon.setText("")
        self.yt_icon.setPixmap(QtGui.QPixmap("./icons/yticon.png"))
        self.yt_icon.setScaledContents(True)
        self.yt_icon.setObjectName("yt_icon")

        self.insta_icon = QtWidgets.QLabel(self.centralwidget)
        self.insta_icon.setGeometry(QtCore.QRect(460, 120, 191, 191))
        self.insta_icon.setText("")
        self.insta_icon.setPixmap(QtGui.QPixmap("./icons/instaicon.png"))
        self.insta_icon.setScaledContents(True)
        self.insta_icon.setObjectName("insta_icon")

        self.yt_button = HoverButton(self.yt_icon, self.centralwidget)
        self.yt_button.setGeometry(QtCore.QRect(70, 130, 261, 171))
        self.yt_button.setStyleSheet("color: rgba(255, 255, 255, 0);\n"
"background-color: rgba(255, 255, 255, 0);")
        self.yt_button.setObjectName("yt_button")
        self.yt_button.clicked.connect(self.on_yt_button_pressed)

        self.insta_button = HoverButton(self.insta_icon, self.centralwidget)
        self.insta_button.setGeometry(QtCore.QRect(470, 130, 181, 171))
        self.insta_button.setStyleSheet("color: rgba(255, 255, 255, 0);\n"
"background-color: rgba(255, 255, 255, 0);")
        self.insta_button.setObjectName("insta_button")
        self.insta_button.clicked.connect(self.on_insta_button_pressed)

        """
        self.yt_text = QtWidgets.QLabel(self.centralwidget)
        self.yt_text.setGeometry(QtCore.QRect(110, 320, 181, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(234, 234, 234))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 18, 18, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.yt_text.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.yt_text.setFont(font)
        self.yt_text.setAlignment(QtCore.Qt.AlignCenter)
        self.yt_text.setObjectName("yt_text")
        
        self.insta_text = QtWidgets.QLabel(self.centralwidget)
        self.insta_text.setGeometry(QtCore.QRect(470, 320, 181, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(234, 234, 234))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 18, 18))

        self.insta_text.setPalette(palette)
        self.insta_text.setFont(font)
        self.insta_text.setAlignment(QtCore.Qt.AlignCenter)
        self.insta_text.setObjectName("insta_text")
        """

        self.yttextField = QtWidgets.QLineEdit(self.centralwidget)
        self.yttextField.setGeometry(QtCore.QRect(65, 330, 280, 31))
        self.yttextField.setStyleSheet("color: #FFFDD0;\nbackground-color: rgba(255, 255, 255, 0);")
        self.yttextField.setPlaceholderText("Enter URL: ")
        self.yttextField.setMaxLength(100)
        self.yttextField.returnPressed.connect(self.on_yt_enter)
        self.yttextField.hide()

        self.instatextField = QtWidgets.QLineEdit(self.centralwidget)
        self.instatextField.setGeometry(QtCore.QRect(430, 330, 250, 31))
        self.instatextField.setStyleSheet("color: #FFFDD0;\nbackground-color: rgba(255, 255, 255, 0);")
        self.instatextField.setPlaceholderText("Enter URL: ")
        self.instatextField.setMaxLength(100)
        self.instatextField.returnPressed.connect(self.on_insta_enter)
        self.instatextField.hide()

        self.yt_mp4 = QtWidgets.QLabel(self.centralwidget)
        self.yt_mp4.setGeometry(QtCore.QRect(110, 380, 70, 45))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.yt_mp4.setFont(font)
        self.yt_mp4.setStyleSheet("""
                                    color: #FFFDD0;
                                    font-weight: bold;
                                    border: 2px solid #FFFDD0;
                                    border-radius: 6px;
                                    padding: 4px;
                                  """)
        self.yt_mp4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.yt_mp4.setText("mp4")
        self.yt_mp4.setScaledContents(True)
        self.yt_mp4.hide()

        self.yt_mp4_button = HoverButton(self.yt_mp4, self.centralwidget)
        self.yt_mp4_button.pressed.connect(self.on_mp4_button_pressed)
        self.yt_mp4_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.yt_mp4_button.setGeometry(110, 380, 70, 45)

        self.yt_mp3 = QtWidgets.QLabel(self.centralwidget)
        self.yt_mp3.setGeometry(QtCore.QRect(220, 380, 70, 45))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.yt_mp3.setFont(font)
        self.yt_mp3.setStyleSheet("""
                                    color: #FFFDD0;
                                    font-weight: bold;
                                    border: 2px solid #FFFDD0;
                                    border-radius: 6px;
                                    padding: 4px;
                                  """)
        self.yt_mp3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.yt_mp3.setText("mp3")
        self.yt_mp3.setScaledContents(True)
        self.yt_mp3.hide()

        self.yt_mp3_button = HoverButton(self.yt_mp3, self.centralwidget)
        self.yt_mp3_button.pressed.connect(self.on_mp3_button_pressed)
        self.yt_mp3_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.yt_mp3_button.setGeometry(220, 380, 70, 45)

        self.insta_download = QtWidgets.QLabel(self.centralwidget)
        self.insta_download.setGeometry(QtCore.QRect(490, 380, 130, 45))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.insta_download.setFont(font)
        self.insta_download.setStyleSheet("""
                                    color: #FFFDD0;
                                    font-weight: bold;
                                    border: 2px solid #FFFDD0;
                                    border-radius: 6px;
                                    padding: 4px;
                                  """)
        self.insta_download.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.insta_download.setText("Download")
        self.insta_download.setScaledContents(True)
        self.insta_download.hide()

        self.insta_download_button = HoverButton(self.insta_download, self.centralwidget)
        self.insta_download_button.pressed.connect(self.insta_download_button_pressed)
        self.insta_download_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.insta_download_button.setGeometry(490, 380, 130, 45)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.yt_button.setText(_translate("MainWindow", "PushButton"))
        self.insta_button.setText(_translate("MainWindow", "PushButton"))

    def on_yt_button_pressed(self):
        self.yttextField.show()
        self.instatextField.hide()
        self.insta_download.hide()

    def on_insta_button_pressed(self):
        self.instatextField.show()
        self.yttextField.hide()
        self.yt_mp4.hide()
        self.yt_mp3.hide()

    def on_yt_enter(self):
        self.url = self.yttextField.text().strip()
        print(self.url)
        self.yt_mp4.show()
        self.yt_mp3.show()

    def on_insta_enter(self):
        self.url = self.instatextField.text().strip()
        print(self.url)
        self.insta_download.show()

    def on_mp3_button_pressed(self):
        Downloader.download_audio(self.url, self.path)

    def on_mp4_button_pressed(self):
        title = Downloader.download_video(self.url, self.path)
        output_filename = title + ".mp4"
        Downloader.remux_streams(self.path, output_filename)

    def insta_download_button_pressed(self):
        Downloader.instagram_downloader(self.url, self.path)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
