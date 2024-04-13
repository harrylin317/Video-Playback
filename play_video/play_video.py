from PyQt5.QtCore import QDir, Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtGui, QtCore
import platform
import sys
import vlc
import os
import pandas as pd
import ast

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
        self.mediaplayer.set_rate(self.mediaplayer.get_rate() * 1.5)

    def SlowDown(self):
        """Slow down the video
        """
        self.mediaplayer.set_rate(self.mediaplayer.get_rate() / 1.5)

class Player(QtWidgets.QMainWindow):
    """A simple Media Player using VLC and Qt
    """

    def __init__(self, segments, filename=None, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")
        self.segments = segments
        # Create a basic vlc instance
        self.instance = vlc.Instance()
        
        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()
        self.is_paused = False

        #set timer
        self.slow_timer = QTimer()
        self.slow_timer.setInterval(100)
        self.slow_timer.timeout.connect(self.checkVideoPosition)

        if filename:
            self.open_file(filename)
            self.play_pause()

    def create_ui(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if platform.system() == "Darwin": # for MacOS
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        self.hbuttonbox = QtWidgets.QHBoxLayout()
        self.playbutton = QtWidgets.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        self.stopbutton = QtWidgets.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.speedupbutton = QtWidgets.QPushButton("Speed Up")
        self.speedupbutton.clicked.connect(self.SpeedUp)
        self.hbuttonbox.addWidget(self.speedupbutton)
        self.slowdownbutton = QtWidgets.QPushButton("Slow Down")
        self.slowdownbutton.clicked.connect(self.SlowDown)
        self.hbuttonbox.addWidget(self.slowdownbutton)


        self.widget.setLayout(self.vboxlayout)

        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Add actions to file menu
        open_action = QtWidgets.QAction("Load Video", self)
        close_action = QtWidgets.QAction("Close App", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        open_action.triggered.connect(self.open_file)
        close_action.triggered.connect(sys.exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def play_pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.is_paused = True
            self.timer.stop()
            self.slow_timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.slow_timer.start()
            self.is_paused = False

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")
    def SpeedUp(self):
        """Speed up the video
        """
        self.mediaplayer.set_rate(self.mediaplayer.get_rate() * 1.5)

    def SlowDown(self):
        """Slow down the video
        """
        self.mediaplayer.set_rate(self.mediaplayer.get_rate() / 1.5)
    def open_file(self, file_path):
        """Open a media file in a MediaPlayer
        """
        if file_path:
            filename = [file_path]
        else:          
            dialog_txt = "Choose Media File"
            filename = QtWidgets.QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
            if not filename:
                return

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(filename[0])

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux": # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows": # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.play_pause()

    def set_volume(self, volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self):
        """Set the movie position according to the position slider.
        """

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.timer.start()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def checkVideoPosition(self):
        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        position = self.mediaplayer.get_time()
        for start, end, slow_rate in self.segments:
            if start <= position <= end:
                self.mediaplayer.set_rate(slow_rate)  # Slow down the video
                break
            else:
                self.mediaplayer.set_rate(1.0)
class PlayVideo:
    def play_video(self, video_path, segments):
        print('Playing Video...')
        app = QApplication(sys.argv)
        # player = VideoWindow(app, video_path, segments)
        # player = VLCPlayer(video_path)
        player = Player(segments=segments,filename=video_path)
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
            if os.path.exists(df_path):
                df = pd.read_csv(df_path)
                segments = df['time+slow'].apply(ast.literal_eval).tolist()
                # segments = [(1, 5.7, 1.7), (20.3, 25.6, 1.2)]
                segments = [(int(start * 1000), int(end * 1000), slow_rate) for start, end, slow_rate in segments]

                status = self.play_video(video_path, segments)
                print(status)
                return status
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip playing video')
            return 0