from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont
import os
from visual import PredictingWidget

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
                background: white;
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

    def enterEvent(self, event):
        if self._default_pos is None:
            self._default_pos = self.pos()

        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(300)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        pos_anim.setStartValue(self.pos())
        pos_anim.setEndValue(self._default_pos - QPoint(0, 8))
        pos_anim.start()

        self.wrapper.setStyleSheet("""
            QFrame#card_wrapper {
                background: white;
                color: black;
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


from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import os


class RecentDataPopup(QWidget):
    def __init__(self, data, on_view=None, on_remove=None, refresh_callback=None):
        super().__init__()
        self.data = data
        self.on_view = on_view
        self.on_remove = on_remove
        self.refresh_callback = refresh_callback

        # === Window setup ===
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(460, 270)

        # === Outer layout (transparent root) ===
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # === Main content container ===
        self.background_frame = QWidget(self)
        self.background_frame.setObjectName("background_frame")

        # subtle drop shadow for floating effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.background_frame.setGraphicsEffect(shadow)

        # === Internal content layout ===
        layout = QVBoxLayout(self.background_frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        # === STYLES ===
        self.setStyleSheet("""
            QWidget#background_frame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(230, 233, 250, 0.9),
                    stop:0.5 rgba(200, 210, 255, 0.95),
                    stop:1 rgba(255, 255, 255, 0.95)
                );
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.4);
            }

            QLabel {
                color: #111;
                font-weight: 500;
                background: transparent;
            }

            QPushButton {
                background-color: white;
                color: #222;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 10px;
                padding: 8px 18px;
                font-size: 12pt;
                font-weight: 500;
                transition: all 200ms ease-in-out;
            }

            QPushButton:hover {
                background-color: rgba(255,255,255,0.9);
                border: 1px solid rgba(0,0,0,0.2);
            }

            QPushButton:pressed {
                background-color: rgba(230,230,230,0.9);
                transform: scale(0.97);
            }
        """)

        # === Labels ===
        name_label = QLabel(f"Name: {data.get('name', 'Unknown')}")
        date_label = QLabel(f"Date Created: {data.get('date', 'N/A')}")
        course_label = QLabel(
            f"Specialized Course: {data.get('specialized_course', 'N/A')} "
            f"({data.get('specialized_course_pct', 0)}%)"
        )
        job_label = QLabel(
            f"Specialized Job: {data.get('specialized_job', 'N/A')} "
            f"({data.get('specialized_job_pct', 0)}%)"
        )

        for lbl in [name_label, date_label, course_label, job_label]:
            lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            layout.addWidget(lbl)

        layout.addStretch()

        # === Buttons ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        view_btn = QPushButton("View Data")
        remove_btn = QPushButton("Remove Data")
        cancel_btn = QPushButton("Cancel")

        btn_layout.addWidget(view_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        outer_layout.addWidget(self.background_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # === Actions ===
        view_btn.clicked.connect(self.view_data)
        remove_btn.clicked.connect(self.remove_data)
        cancel_btn.clicked.connect(self.close)

    def view_data(self):
        file_path = self.data.get("file_path")
        if self.on_view:
            self.on_view(self.data, file_path)
        self.close()

    def remove_data(self):
        try:
            file_path = self.data.get("file_path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"[OK] Deleted {file_path}")
                QMessageBox.information(self, "Removed", "Data file removed successfully.")
                if self.refresh_callback:
                    self.refresh_callback()
                if self.on_remove:
                    self.on_remove(self.data)
            else:
                QMessageBox.warning(self, "Error", "File not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")
        self.close()


