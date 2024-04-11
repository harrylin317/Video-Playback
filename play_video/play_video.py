from PyQt5.QtCore import QDir, Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtGui

import sys
import vlc

class VideoWindow(QMainWindow):

    def __init__(self, app, video_path, segments, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.app = app
        self.segments = segments
        self.setWindowTitle("Video Player") 
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        #set timer
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.checkVideoPosition)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Create new action
        # openAction = QAction(QIcon('open.png'), '&Open', self)        
        # openAction.setShortcut('Ctrl+O')
        # openAction.setStatusTip('Open movie')
        # openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create buttons for slowing down and speeding up the video
        self.slowButton = QPushButton("Slow Down")
        self.slowButton.clicked.connect(self.slowDown)
        self.fastButton = QPushButton("Speed Up")
        self.fastButton.clicked.connect(self.speedUp)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&Options')
        # fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.slowButton)  
        controlLayout.addWidget(self.fastButton)  
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        if video_path is not None:
            self.openFile(video_path)

    def openFile(self, file_path):
        # if file_path is None:
        #     file_path, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if file_path != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.playButton.setEnabled(True)
        else:
            print('Video file not found')
            self.exitCall()

    def exitCall(self):
        self.app.exit()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            # self.timer.stop()
        else:
            self.mediaPlayer.play()
            # self.timer.start(1000)
    def slowDown(self):
        self.mediaPlayer.setPlaybackRate(0.5)

    def speedUp(self):
        self.mediaPlayer.setPlaybackRate(2.0)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def checkVideoPosition(self):
        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        position = self.mediaPlayer.position()
        for start, end in self.segments:
            if start <= position <= end:
                self.mediaPlayer.setPlaybackRate(0.5)  # Slow down the video
                break
            else:
                self.mediaPlayer.setPlaybackRate(1.0)
class VLCPlayer(QMainWindow):
    def __init__(self, video_path, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        # Creating VLC player
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        media = self.instance.media_new(video_path)
        self.mediaplayer.set_media(media)
        # Creating buttons
        self.playbutton = QtWidgets.QPushButton("Play")
        self.playbutton.clicked.connect(self.PlayPause)

        self.speedupbutton = QtWidgets.QPushButton("Speed Up")
        self.speedupbutton.clicked.connect(self.SpeedUp)

        self.slowdownbutton = QtWidgets.QPushButton("Slow Down")
        self.slowdownbutton.clicked.connect(self.SlowDown)

        # Setting up layout
        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.addWidget(self.playbutton)
        vboxlayout.addWidget(self.speedupbutton)
        vboxlayout.addWidget(self.slowdownbutton)

        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)
        widget.setLayout(vboxlayout)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
        else:
            self.mediaplayer.play()
            self.playbutton.setText("Pause")

    def SpeedUp(self):
        """Speed up the video
        """
        self.mediaplayer.set_rate(self.mediaplayer.get_rate() * 2)

    def SlowDown(self):
        """Slow down the video
        """
        self.mediaplayer.set_rate(self.mediaplayer.get_rate() / 2)

class PlayVideo:
    def play_video(self, video_path, segments):
        print('Playing Video...')
        segments = [(int(start * 1000), int(end * 1000)) for start, end in segments]
        app = QApplication(sys.argv)
        # player = VideoWindow(app, video_path, segments)
        player = VLCPlayer(video_path)
        player.resize(640, 480)
        player.show()
        ret = app.exec_()
        if ret == 0:
            print("Video played successfully.")
            return 0
        else:
            print(f"Error occurred when playing video: {ret}")
            return -1

    def process(self, args):
        if args['run_video_player']:
            df_path = args['df_path']
            video_path = args['video_path']
            segments = [(1, 5.7), (20.3, 25.6)]
            status = self.play_video(video_path, segments)
            print(status)
            return status
        else:
            print('Skip playing video')
            return 0