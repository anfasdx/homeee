from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPoint

class Whiteboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 800, 600)

        self.last_pos = None  # Track the last drawn position
        self.pen = QPen(QColor("black"), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def update_camera_feed(self, frame):
        """Update camera feed onto the whiteboard."""
        if frame is not None:
            height, width, channels = frame.shape
            img = QImage(frame.data, width, height, channels * width, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)

    def mousePressEvent(self, event):
        """Start drawing."""
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Continue drawing."""
        if event.buttons() == Qt.LeftButton and self.last_pos is not None:
            painter = QPainter(self.view.viewport())
            painter.setPen(self.pen)
            painter.drawLine(self.last_pos, event.pos())
            self.last_pos = event.pos()
            painter.end()

    def mouseReleaseEvent(self, event):
        """Stop drawing."""
        if event.button() == Qt.LeftButton:
            self.last_pos = None
