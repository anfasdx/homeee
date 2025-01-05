import cv2
from PySide6.QtCore import QThread, Signal
from gesture import GestureDetection

class CameraThread(QThread):
    frame_available = Signal(object)

    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)
        self.gesture_detection = GestureDetection()
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                frame = self.gesture_detection.detect_gesture(frame)
                frame = cv2.flip(frame, 1)
                self.frame_available.emit(frame)

    def stop(self):
        self.running = False
        self.capture.release()
        self.gesture_detection.release()
        self.quit()
