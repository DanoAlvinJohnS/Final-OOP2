from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QRegion


class FancyCircularProgress(QWidget):
    def __init__(self, parent=None, animation_duration=800, inner_gap=12, inner_color=QColor(255, 255, 255)):
        super().__init__(parent)
        self._value = 0.0
        self._max = 100.0
        self._inner_gap = inner_gap
        self._inner_color = inner_color
        self.setMinimumSize(220, 220)

        # center label
        self.label = QLabel("0%", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # animation
        self.anim = QVariantAnimation(self)
        self.anim.valueChanged.connect(self._on_anim_value_changed)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.setDuration(animation_duration)

    # ----- API -----
    def setTargetValue(self, target: float, duration: int | None = None):
        target = max(0.0, min(self._max, float(target)))
        if duration is not None:
            self.anim.setDuration(duration)
        self.anim.stop()
        self.anim.setStartValue(self._value)
        self.anim.setEndValue(target)
        self.anim.start()

    def value(self) -> float:
        return float(self._value)

    def setMaximum(self, max_val: float):
        self._max = max_val

    def setInnerGap(self, gap: int):
        """Set spacing between ring and inner circle (bigger = smaller inner circle)."""
        self._inner_gap = max(0, gap)
        self.update()

    def setInnerColor(self, color: QColor):
        """Set background color of inner circle."""
        self._inner_color = QColor(color)
        self.update()

    # ----- Internal -----
    def _on_anim_value_changed(self, v):
        self._value = float(v)
        self.label.setText(f"{int(round(self._value))}%")
        self.update()

    def progress_color(self, v: float) -> QColor:
        if v <= 20:  return QColor(255, 77, 77)   # red
        if v <= 50:  return QColor(255, 200, 0)   # yellow
        if v <= 80:  return QColor(0, 200, 83)    # green
        return QColor(63, 114, 255)               # blue

    # ----- Painting -----
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # enforce circular clipping (no box edges!)
        size = min(self.width(), self.height())
        region = QRegion(self.rect(), QRegion.RegionType.Ellipse)
        self.setMask(region)

        # background (outermost circle)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)

        # geometry
        margin = max(10, int(size * 0.08))
        pen_width = max(12, int(size * 0.1))
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)

        # track arc
        track_pen = QPen(QColor(235, 235, 235), pen_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 16 * 360)

        # progress arc
        angle = int(16 * 360 * (self._value / self._max))
        base_color = self.progress_color(self._value)

        prog_pen = QPen(base_color, pen_width)
        prog_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(prog_pen)
        painter.drawArc(rect, -90 * 16, -angle)

        # ---- Inner circle ----
        ring_thickness = pen_width
        inner_diameter = size - (2 * margin + ring_thickness + self._inner_gap * 2)

        inner_rect = QRectF(
            (size - inner_diameter) / 2,
            (size - inner_diameter) / 2,
            inner_diameter,
            inner_diameter
        )

        painter.setBrush(QBrush(self._inner_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(inner_rect)

        # label in center
        lbl_w, lbl_h = int(inner_rect.width()), int(inner_rect.height())
        self.label.setGeometry(int(inner_rect.x()), int(inner_rect.y()), lbl_w, lbl_h)

        font_size = max(10, int(lbl_h * 0.3))
        self.label.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
        self.label.setStyleSheet(
            f"QLabel{{background: transparent; border-radius: {int(lbl_w/2)}px; color: #222}}"
        )
