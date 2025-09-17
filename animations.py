from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, QMainWindow
from PyQt6.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QPainterPath

class FancyCircularProgress(QWidget):
    def __init__(self, percentage=0, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._max = 100.0

        self.setMinimumSize(180, 180)

        # percentage label (center)
        self.label = QLabel("0%", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # animation
        self.anim = QVariantAnimation(self)
        self.anim.valueChanged.connect(self._on_anim_value_changed)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.setDuration(800)

        # set initial value
        self.setTargetValue(percentage, 1300)

    # ----- Animation -----
    def setTargetValue(self, target: float, duration: int | None = None):
        target = max(0.0, min(self._max, float(target)))
        if duration is not None:
            self.anim.setDuration(duration)
        self.anim.stop()
        self.anim.setStartValue(self._value)
        self.anim.setEndValue(target)
        self.anim.start()

    def _on_anim_value_changed(self, v):
        self._value = float(v)
        self.label.setText(f"{int(round(self._value))}%")
        self.update()

    def value(self) -> float:
        return float(self._value)

    # ----- Colors -----
    def progress_color(self, v: float) -> QColor:
        if v <= 20:  return QColor(255, 77, 77)   # red
        if v <= 50:  return QColor(255, 200, 0)   # yellow
        if v <= 80:  return QColor(0, 200, 83)    # green
        return QColor(63, 114, 255)               # blue

    # ----- Painting -----
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # circular clipping
        clip_path = QPainterPath()
        clip_path.addEllipse(0, 0, w, h)
        painter.setClipPath(clip_path)

        outer_margin = max(8, int(min(w, h) * 0.07))
        pen_width = max(10, int(min(w, h) * 0.08))
        rect = QRectF(outer_margin, outer_margin, w - 2 * outer_margin, h - 2 * outer_margin)

        # background track
        track_pen = QPen(QColor(240, 240, 240), pen_width * 2)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 16 * 360)

        size = min(self.width(), self.height())
        inner_gap = int(size * 0.07)  # adjust thickness of ring
        inner_margin = outer_margin + pen_width + inner_gap
        inner_rect = QRectF(inner_margin, inner_margin,
                            size - 2 * inner_margin, size - 2 * inner_margin)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(inner_rect)

        # progress
        angle = int(16 * 360 * (self._value / self._max))
        base_color = self.progress_color(self._value)

        # glow halo
        glow_pen = QPen(base_color, pen_width + 12)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        glow_pen.setColor(QColor(base_color.red(), base_color.green(), base_color.blue(), 70))
        painter.setPen(glow_pen)
        painter.drawArc(rect, -90 * 16, -angle)

        # main arc
        prog_pen = QPen(base_color, pen_width)
        prog_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(prog_pen)
        painter.drawArc(rect, -90 * 16, -angle)

        # label geometry
        inner_margin = pen_width + 24
        inner_rect = QRectF(inner_margin, inner_margin, w - 2 * inner_margin, h - 2 * inner_margin)
        lbl_w, lbl_h = int(inner_rect.width()), int(inner_rect.height())
        self.label.setGeometry(int(inner_rect.x()), int(inner_rect.y()), lbl_w, lbl_h)

        font_size = max(10, int(lbl_h * 0.28))
        self.label.setStyleSheet(
            f"QLabel{{background: transparent; font: bold {font_size}px Arial; color: #222}}"
        )

