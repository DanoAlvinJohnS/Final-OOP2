from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QGraphicsTextItem, QGraphicsView,
    QGraphicsScene, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF, QPoint,
    QRandomGenerator, pyqtSignal, pyqtProperty, QParallelAnimationGroup
)
from PyQt6.QtGui import QFont, QBrush, QColor
from dashboard_gui import login_window, DashboardWidget
from PyQt6 import uic

# ---------- Animated Text Item ----------
class AnimatedTextItem(QGraphicsTextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scale = 1.0
        self._rotation = 0.0
        self._opacity = 1.0

    # ---- Opacity ----
    def get_opacity_anim(self):
        return self._opacity

    def set_opacity_anim(self, value):
        self._opacity = value
        self.setOpacity(value)

    opacity_anim = pyqtProperty(float, fget=get_opacity_anim, fset=set_opacity_anim)
    
    # ---- Scale ----
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

        self.setStyleSheet("background-color: #b8e2f4;")

        # Graphics view + scene
        self.view = QGraphicsView(self)
        self.view.setGeometry(self.rect())
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # Background
        self.bg_color = QColor("#ffffff")
        self.scene.setBackgroundBrush(QBrush(self.bg_color))
        self.view = QGraphicsView(self)
        self.view.setGeometry(self.rect())
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

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

            # --- light blue (#b8e2f4) to dark navy (#0d1b2a) ---
            r = int(184 + (13 - 184) * self.bg_progress / 100)
            g = int(226 + (27 - 226) * self.bg_progress / 100)
            b = int(244 + (42 - 244) * self.bg_progress / 100)
            self.bg_color = QColor(r, g, b)
            self.scene.setBackgroundBrush(QBrush(self.bg_color))

            # --- dark navy (#0d1b2a) to light blue (#b8e2f4) ---
            tr = int(13 + (184 - 13) * self.bg_progress / 100)
            tg = int(27 + (226 - 27) * self.bg_progress / 100)
            tb = int(42 + (244 - 42) * self.bg_progress / 100)
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


class CareerExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Career Explorer")
        self.resize(1500, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container.setStyleSheet("background-color: white;")

        self.login_widget = login_window(self)
        self.container_layout.addWidget(self.login_widget)
        self.login_widget.login_btn.clicked.connect(self.login)

        self.wrapper = QWidget(self)
        self.wrapper_layout = QVBoxLayout(self.wrapper)
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.wrapper_layout.addWidget(self.container)

        self.container.hide()
        self.setCentralWidget(self.wrapper)

        self.overlay = PlayfulSplash(self)
        self.overlay.show()

    def login(self):
        username = self.login_widget.login_input.text()
        password = self.login_widget.password_input.text()

        if username == "admin" and password == "password":
            print("Login successful!")
            self.container_layout.removeWidget(self.login_widget)
            self.login_widget.deleteLater()

            self.dashboard_widget = DashboardWidget(self)
            self.container_layout.addWidget(self.dashboard_widget)
            self.dashboard_widget.show()
        else:
            print("Invalid credentials. Please try again.")

