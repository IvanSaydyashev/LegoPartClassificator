from PyQt5 import QtCore, QtGui, uic, QtWidgets
import sys
import cv2
import threading
import queue
import db.dbmanager
from ultralytics import YOLO

model_ev3 = YOLO('weights/ev3.pt')

running = False
capture_thread = None
form_class = uic.loadUiType("ui/simple.ui")[0]


def grab(cam, frame_queue, width, height, fps):
    global running
    capture = cv2.VideoCapture(cam)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)

    while running:
        frame = {}
        capture.grab()
        retval, img = capture.retrieve(0)
        frame["img"] = img
        if frame_queue.qsize() < 10:
            frame_queue.put(frame)
        else:
            frame_queue.qsize()

        if not running:
            break


class OwnImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


class MyWindowClass(QtWidgets.QMainWindow, form_class):
    global running, q, gray_filter_flag
    running = False
    gray_filter_flag = False
    q = queue.Queue()

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.startButton.clicked.connect(self.video_state)
        self.BlaWhCheck.stateChanged.connect(self.gray_filter)

        self.window_width = self.RawImageWidget.frameSize().width()
        self.window_height = self.RawImageWidget.frameSize().height()
        self.RawImgWidget = OwnImageWidget(self.RawImageWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)



    def gray_filter(self, checked):
        global gray_filter_flag
        if checked == 2:
            gray_filter_flag = True
        else:
            gray_filter_flag = False

    def video_state(self):
        global running, q
        capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))
        if not running:
            running = True
            capture_thread.start()
            self.startButton.setEnabled(False)
            self.startButton.setText('Starting...')
        else:
            running = False
            self.startButton.setEnabled(False)
            self.startButton.setText("Stopping...")

    def update_frame(self):
        def getColours(cls_num):
            base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            color_index = cls_num % len(base_colors)
            increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
            color = [base_colors[color_index][i] + increments[color_index][i] *
                     (cls_num // len(base_colors)) % 256 for i in range(3)]
            return tuple(color)

        global gray_filter_flag
        if not q.empty():
            self.startButton.setEnabled(True)

            if running:
                self.startButton.setText('Stop video')
            else:
                self.startButton.setText('Start video')

            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1

            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            results = model_ev3.track(img, stream=True)
            for result in results:
                classes_names = result.names

                # iterate over each box
                for box in result.boxes:
                    # check if confidence is greater than 40 percent
                    if box.conf[0] > 0.4:
                        # get coordinates
                        [x1, y1, x2, y2] = box.xyxy[0]
                        # convert to int
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        # get the class
                        cls = int(box.cls[0])

                        # get the class name
                        class_name = classes_names[cls]

                        # get the respective colour
                        colour = getColours(cls)

                        # draw the rectangle
                        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

                        # put the class name and confidence on the image
                        cv2.putText(frame, f'{classes_names[int(box.cls[0])]} {box.conf[0]:.2f}', (x1, y1),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
            if gray_filter_flag:
                image = image.convertToFormat(QtGui.QImage.Format_Grayscale8)
            self.RawImgWidget.setImage(image)

    def closeEvent(self, event):
        global running
        running = False


app = QtWidgets.QApplication(sys.argv)
w = MyWindowClass(None)
w.setWindowTitle('AI Lego')
w.show()
app.exec_()
