import sys
import cv2
from PySide6.QtCore import Qt, Signal, QThread, QFile, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QFileDialog
from PySide6.QtGui import QImage, QPixmap, QPen, QColor, QPainter, QMouseEvent
from PySide6 import QtUiTools

class CameraThread(QThread):
    frame_available = Signal(object)

    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.frame_available.emit(frame)

    def stop(self):
        self.running = False
        self.capture.release()
        self.wait()  # Ensure the thread has finished before quitting

class DrawingCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.drawing = False
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3
        self.current_item = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_pos = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            current_pos = self.mapToScene(event.pos())
            line_item = QGraphicsLineItem(self.last_pos.x(), self.last_pos.y(), current_pos.x(), current_pos.y())
            line_item.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
            self.scene.addItem(line_item)
            self.last_pos = current_pos

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def set_pen(self, color, width):
        self.pen_color = color
        self.pen_width = width

    def clear_canvas(self):
        self.scene.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.camera_thread = CameraThread()
        self.camera_thread.frame_available.connect(self.update_camera_feed)
        self.camera_thread.start()
        self.penButton.clicked.connect(self.set_pen)
        self.eraserButton.clicked.connect(self.set_eraser)
        self.clearButton.clicked.connect(self.clear_canvas)
        self.saveButton.clicked.connect(self.save_canvas)  # Added missing connection for saveButton
        self.drawing_mode = 'pen'
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3

    def setup_ui(self):
        loader = QtUiTools.QUiLoader()
        ui_file = QFile("ui/main_ui.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.videoLabel = self.ui.findChild(QLabel, 'videoLabel')
        self.penButton = self.ui.findChild(QPushButton, 'penButton')
        self.eraserButton = self.ui.findChild(QPushButton, 'eraserButton')
        self.saveButton = self.ui.findChild(QPushButton, 'saveButton')
        self.clearButton = self.ui.findChild(QPushButton, 'clearButton')
        self.drawing_canvas = DrawingCanvas(self)
        self.drawing_canvas.setGeometry(10, 50, 780, 500)
        self.drawing_canvas.setStyleSheet("background: transparent; border: none;")
        self.videoLabel.setGeometry(10, 50, 780, 500)

    def update_camera_feed(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_img)
        self.videoLabel.setPixmap(pixmap)

    def set_pen(self):
        self.drawing_mode = 'pen'
        self.drawing_canvas.set_pen(QColor(0, 0, 0), 3)

    def set_eraser(self):
        self.drawing_mode = 'eraser'
        self.drawing_canvas.set_pen(QColor(255, 255, 255), 15)

    def clear_canvas(self):
        self.drawing_canvas.clear_canvas()

    def save_canvas(self):
        # Implement the save functionality here
        image = QImage(self.drawing_canvas.viewport().size(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self.drawing_canvas.render(painter)
        painter.end()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
        if file_path:
            image.save(file_path)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
