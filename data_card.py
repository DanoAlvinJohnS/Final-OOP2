from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor

class DataCard(QWidget):
    """
    Modern clickable card with animated gradient hover and no shadow.
    """
    def __init__(self, data: dict, parent_width: int = 1000, on_click=None):
        super().__init__()
        self.data = data
        self.on_click = on_click

        # sizing
        card_w = max(160, parent_width // 5)
        self.setFixedWidth(card_w)
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # outer layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---- Wrapper ----
        self.wrapper = QFrame(self)
        self.wrapper.setObjectName("card_wrapper")
        self.wrapper.setStyleSheet("""
            QFrame#card_wrapper {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #c2e9fb
                );
                border-radius: 20px;
                border: 2px solid rgba(255,255,255,0.12);
            }
        """)
        self.wrapper.setFixedSize(card_w, self.minimumHeight())
        wrapper_layout = QVBoxLayout(self.wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        # ---- Content ----
        content = QWidget(self.wrapper)
        content.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(6)

        title = QLabel(str(data.get("name", "Unknown")))
        date = QLabel(f"Date: {data.get('date', '')}")
        specialized = QLabel(
            f"Specialized course: {data.get('specialized_course','N/A')}, {data.get('specialized_course_pct',0)}%\n"
            f"Specialized job: {data.get('specialized_job','N/A')}, {data.get('specialized_job_pct',0)}%"
        )

        title.setStyleSheet("""
            background: transparent;
            color: #0D1B2A;
            font-weight: 600;
            font-size: 14px;
        """)
        date.setStyleSheet("""
            background: transparent;
            color: #1E2A3A;
            font-size: 12px;
        """)
        specialized.setStyleSheet("""
            background: transparent;
            color: #000000;
            font-size: 12px;
            font-weight: 500;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        date.setAlignment(Qt.AlignmentFlag.AlignLeft)
        specialized.setAlignment(Qt.AlignmentFlag.AlignLeft)

        content_layout.addWidget(title)
        content_layout.addWidget(date)
        content_layout.addWidget(specialized)
        content_layout.addStretch()
        wrapper_layout.addWidget(content)

        # ---- Overlay button ----
        overlay_btn = QPushButton(self.wrapper)
        overlay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        overlay_btn.setFlat(True)
        overlay_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        overlay_btn.setGeometry(0, 0, self.wrapper.width(), self.wrapper.height())
        overlay_btn.raise_()
        if self.on_click:
            overlay_btn.clicked.connect(lambda: self.on_click(self.data))

        self._overlay = overlay_btn
        outer.addWidget(self.wrapper, alignment=Qt.AlignmentFlag.AlignLeft)

        self._default_pos = None
        self._bg_anim = None

    # ---------- Hover Effects ----------
    def enterEvent(self, event):
        if self._default_pos is None:
            self._default_pos = self.pos()

        # lift card up
        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(300)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        pos_anim.setStartValue(self.pos())
        pos_anim.setEndValue(self._default_pos - QPoint(0, 8))
        pos_anim.start()

        # background transition
        self.wrapper.setStyleSheet("""
            QFrame#card_wrapper {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #a1c4fd
                );
                border-radius: 20px;
                border: 2px solid rgba(255,255,255,0.12);
            }
        """)

        self._pos_anim = pos_anim
        return super().enterEvent(event)

    def leaveEvent(self, event):
        if self._default_pos is None:
            return super().leaveEvent(event)

        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(300)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        pos_anim.setStartValue(self.pos())
        pos_anim.setEndValue(self._default_pos)
        pos_anim.start()

        self.wrapper.setStyleSheet("""
            QFrame#card_wrapper {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #c2e9fb
                );
                border-radius: 20px;
                border: 2px solid rgba(255,255,255,0.12);
            }
        """)

        self._pos_anim = pos_anim
        return super().leaveEvent(event)
