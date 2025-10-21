from PyQt6.QtCore import (
    Qt,    QPoint,    QPointF,
    QRect,    QRectF,    QTimer,
    QRandomGenerator,    QVariantAnimation,     QPropertyAnimation,
    QEasingCurve,    pyqtSignal,    pyqtProperty,
    QParallelAnimationGroup,
)

from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QFont, QPainterPath,
)

from PyQt6.QtWidgets import (
    QWidget, QLabel, QGraphicsView,
    QGraphicsScene, QGraphicsTextItem, QGraphicsOpacityEffect,
)

class FancyCircularProgress(QWidget):
    def __init__(self, percentage=0, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._max = 100.0

        self.setMinimumSize(180, 180)

        self.label = QLabel("0%", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.anim = QVariantAnimation(self)
        self.anim.valueChanged.connect(self._on_anim_value_changed)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.setDuration(800)

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
        # Define key colors
        red = QColor(255, 77, 77)
        yellow = QColor(255, 200, 0)
        green = QColor(0, 200, 83)
        blue = QColor(33, 150, 243)

        # Linear interpolation helper
        def lerp(c1, c2, t):
            r = c1.red() + (c2.red() - c1.red()) * t
            g = c1.green() + (c2.green() - c1.green()) * t
            b = c1.blue() + (c2.blue() - c1.blue()) * t
            return QColor(int(r), int(g), int(b))

        if v <= 20:
            return lerp(red, yellow, v / 20.0)
        elif v <= 50:
            return lerp(yellow, green, (v - 20) / 30.0)
        elif v <= 80:
            return lerp(green, blue, (v - 50) / 30.0)
        else:
            return blue


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

def switch_widget(self, old_widget, new_widget, direction="left"):
        """Smoothly transitions between two widgets in the given direction."""
        if not old_widget or not new_widget:
            return

        # Ensure both widgets are in the container
        if self.container_layout.indexOf(new_widget) == -1:
            self.container_layout.addWidget(new_widget)

        container_rect = self.container.geometry()
        width = container_rect.width()
        height = container_rect.height()

        # Initial positions based on direction
        if direction == "left":
            start_geo = QRect(width, 0, width, height)
            end_geo = QRect(0, 0, width, height)
        elif direction == "right":
            start_geo = QRect(-width, 0, width, height)
            end_geo = QRect(0, 0, width, height)
        elif direction == "up":
            start_geo = QRect(0, height, width, height)
            end_geo = QRect(0, 0, width, height)
        elif direction == "down":
            start_geo = QRect(0, -height, width, height)
            end_geo = QRect(0, 0, width, height)
        else:
            return

        new_widget.setGeometry(start_geo)
        new_widget.show()

        # Animation setup
        anim = QPropertyAnimation(new_widget, b"geometry")
        anim.setDuration(600)
        anim.setStartValue(start_geo)
        anim.setEndValue(end_geo)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

        # Hide old widget after animation
        old_widget.hide()
        self._current_animation = anim
        
def shake_window(self):
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(500)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        current_pos = self.pos()
        offset = 10  # shake distance

        # Define start and end
        animation.setStartValue(current_pos)
        animation.setEndValue(current_pos)  # must have end value

        # Add keyframes for shaking motion
        animation.setKeyValueAt(0.1, current_pos + QPoint(-offset, 0))
        animation.setKeyValueAt(0.2, current_pos + QPoint(offset, 0))
        animation.setKeyValueAt(0.3, current_pos + QPoint(-offset, 0))
        animation.setKeyValueAt(0.4, current_pos + QPoint(offset, 0))
        animation.setKeyValueAt(0.5, current_pos)

        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._shake_anim = animation

class AnimatedTextItem(QGraphicsTextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scale = 1.0
        self._rotation = 0.0
        self._opacity = 1.0

    def get_opacity_anim(self):
        return self._opacity

    def set_opacity_anim(self, value):
        self._opacity = value
        self.setOpacity(value)

    opacity_anim = pyqtProperty(float, fget=get_opacity_anim, fset=set_opacity_anim)
    
    def get_scale_anim(self):
        return self._scale

    def set_scale_anim(self, value):
        self._scale = value
        self.setScale(value)

    scale_anim = pyqtProperty(float, fget=get_scale_anim, fset=set_scale_anim)

    # ---- Rotation ----
    def get_rotation_anim(self):
        return self._rotation

    def set_rotation_anim(self, value):
        self._rotation = value
        self.setRotation(value)

    rotation_anim = pyqtProperty(float, fget=get_rotation_anim, fset=set_rotation_anim)


# ---------- Splash Screen ----------
class PlayfulSplash(QWidget):
    splash_done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent:
            self.setGeometry(parent.rect())

        # --- INITIAL BACKGROUND (start white) ---
        self.setStyleSheet("background-color: white;")

        # --- Create one GraphicsView and Scene ---
        self.view = QGraphicsView(self)
        self.view.setGeometry(self.rect())
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # --- Start background color ---
        self.bg_color = QColor("#ffffff")  # start white
        self.scene.setBackgroundBrush(QBrush(self.bg_color))


        # TITLE w animatable properties
        self.title = AnimatedTextItem("Career Explorer")
        self.title.setFont(QFont("Helvetica", 70, QFont.Weight.Bold))
        self.title.setDefaultTextColor(QColor("#0d1b2a"))
        self.title.set_opacity_anim(0)
        self.title.setTransformOriginPoint(self.title.boundingRect().center())
        self.scene.addItem(self.title)

        # For background transition
        self.bg_timer = QTimer()
        self.bg_timer.timeout.connect(self.update_bg)
        self.bg_progress = 0

        # Start after short delay
        QTimer.singleShot(300, self.start_title_animation)

    def center_title(self):
        rect = self.title.boundingRect()
        self.title.setPos(
            (self.width() - rect.width()) / 2,
            (self.height() - rect.height()) / 2
        )

    def start_title_animation(self):
        self.scene.setSceneRect(0, 0, self.width(), self.height())
        self.center_title()

        # --- Fade in ---
        self.fade_anim = QPropertyAnimation(self.title, b"opacity_anim")
        self.fade_anim.setDuration(1200)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)

        # --- Scale overshoot ---
        self.scale_anim = QPropertyAnimation(self.title, b"scale_anim")
        self.scale_anim.setDuration(800)
        self.scale_anim.setStartValue(0.05)
        self.scale_anim.setEndValue(2)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # --- Rotate ---
        self.rotate_anim = QPropertyAnimation(self.title, b"rotation_anim")
        self.rotate_anim.setDuration(800)
        self.rotate_anim.setStartValue(32)
        self.rotate_anim.setEndValue(0)
        self.rotate_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # --- Settle to 1.0 scale ---
        self.settle_anim = QPropertyAnimation(self.title, b"scale_anim")
        self.settle_anim.setDuration(400)
        self.settle_anim.setStartValue(2.0)
        self.settle_anim.setEndValue(1.0)
        self.settle_anim.setEasingCurve(QEasingCurve.Type.OutBounce)

        # Start all
        self.fade_anim.start()
        self.scale_anim.start()
        self.rotate_anim.start()

        self.scale_anim.finished.connect(self.on_title_settled)

    def on_title_settled(self):
        self.settle_anim.start()
        self.bg_timer.start(30)  # begin background color transition
        self.spawn_shapes()
        QTimer.singleShot(3000, self.start_dashboard_animation)

    def start_dashboard_animation(self):
        parent = self.parent()
        if not parent:
            return

        target = parent.container

        wrapper = getattr(parent, "wrapper", None)
        wrapper_layout = getattr(parent, "wrapper_layout", None)
        try:
            if wrapper_layout is not None:
                wrapper_layout.removeWidget(target)
        except Exception:
            pass

        target.setParent(parent)
        target.resize(parent.width(), parent.height())
        target.show()
        target.raise_()

        start_pos = QPoint(-parent.width(), 0)
        end_pos = QPoint(0, 0)
        target.move(start_pos)

        # -------- Title slide out to the RIGHT (ease-out) --------
        cur_title_pos = self.title.pos()
        title_width = self.title.boundingRect().width()
        end_title_x = parent.width() + title_width + 20
        end_title_pos = QPointF(end_title_x, cur_title_pos.y())

        title_slide = QPropertyAnimation(self.title, b"pos")
        title_slide.setDuration(1000)   
        title_slide.setStartValue(cur_title_pos)
        title_slide.setEndValue(end_title_pos)
        title_slide.setEasingCurve(QEasingCurve.Type.InCubic)  

        # -------- Dashboard slide IN from left (ease-in) --------
        dash_slide = QPropertyAnimation(target, b"pos")
        dash_slide.setDuration(2000)  
        dash_slide.setStartValue(start_pos)
        dash_slide.setEndValue(end_pos)
        dash_slide.setEasingCurve(QEasingCurve.Type.InQuad)  

        # -------- Run both together and keep references --------
        self._anim_group = QParallelAnimationGroup(self)
        self._anim_group.addAnimation(title_slide)
        self._anim_group.addAnimation(dash_slide)

        def _on_finished():
            try:
                if wrapper is not None and wrapper_layout is not None:
                    target.setParent(wrapper)
                    wrapper_layout.addWidget(target)
                    target.show()
                else:
                    target.move(0, 0)
            finally:
                self.close()
                self.splash_done.emit()

        self._anim_group.finished.connect(_on_finished)
        self._anim_group.start()

    def update_bg(self):
        if self.bg_progress < 100:
            self.bg_progress += 2

            # --- white (#ffffff) to dark navy (#0d1b2a) ---
            r = int(255 + (13 - 255) * self.bg_progress / 100)
            g = int(255 + (27 - 255) * self.bg_progress / 100)
            b = int(255 + (42 - 255) * self.bg_progress / 100)
            self.bg_color = QColor(r, g, b)
            self.scene.setBackgroundBrush(QBrush(self.bg_color))

            # --- dark navy (#0d1b2a) to white (#ffffff) for title text ---
            tr = int(13 + (255 - 13) * self.bg_progress / 100)
            tg = int(27 + (255 - 27) * self.bg_progress / 100)
            tb = int(42 + (255 - 42) * self.bg_progress / 100)
            self.title.setDefaultTextColor(QColor(tr, tg, tb))
        else:
            self.bg_timer.stop()

    def spawn_shapes(self, count: int = 50):
        self.shape_anims = []
        center = self.scene.sceneRect().center()
        texts = ["X", "O", "☐"]  

        for i in range(count):
            text = texts[i % 3]  # alternate 

            shape = QGraphicsTextItem(text)
            shape.setDefaultTextColor(Qt.GlobalColor.white)
            shape.setFont(QFont("Arial", 30))
            shape.setOpacity(5.0)
            shape.setPos(center - QPointF(shape.boundingRect().width() / 2,
                                        shape.boundingRect().height() / 2))
            self.scene.addItem(shape)
            shape.setScale(0.1)

            # Scale animation
            scale_anim = QPropertyAnimation(shape, b"scale")
            scale_anim.setDuration(500)
            scale_anim.setStartValue(0.1)
            scale_anim.setEndValue(0.8)
            scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

            # Move animation
            end_x = center.x() + QRandomGenerator.global_().bounded(-1000, 1000)
            end_y = center.y() + QRandomGenerator.global_().bounded(-750, 750)
            move_anim = QPropertyAnimation(shape, b"pos")
            move_anim.setDuration(3000)
            move_anim.setStartValue(shape.pos())
            move_anim.setEndValue(QPointF(end_x, end_y))
            move_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            # Fade animation
            effect = QGraphicsOpacityEffect()
            shape.setGraphicsEffect(effect)
            fade_anim = QPropertyAnimation(effect, b"opacity")
            fade_anim.setDuration(2000)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            
            # Rotation animation
            rot_anim = QPropertyAnimation(shape, b"rotation")
            rot_anim.setDuration(1500)
            rot_anim.setStartValue(0)
            rot_anim.setEndValue(QRandomGenerator.global_().bounded(-180, 180))
            rot_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            self.shape_anims.append((scale_anim, move_anim, fade_anim, rot_anim))
            scale_anim.start()
            move_anim.start()
            fade_anim.start()
            rot_anim.start()

