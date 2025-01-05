import cv2
from PySide6.QtCore import QThread, Signal

class CameraThread(QThread):
    # Signal to send the frame to the main thread
    frame_available = Signal(object)

    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)
        self.frame = None

    def run(self):
        while True:
            ret, frame = self.capture.read()
            if ret:
                # Flip the frame horizontally to mirror it
                frame = cv2.flip(frame, 1)
                self.frame = frame
                self.frame_available.emit(frame)

    def stop(self):
        self.capture.release()
        self.quit()
