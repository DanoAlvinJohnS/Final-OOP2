from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QGraphicsTextItem, QGraphicsView,
    QGraphicsScene, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF, QPoint,
    QRandomGenerator, pyqtSignal, pyqtProperty, QParallelAnimationGroup, QPropertyAnimation, QPoint
)

from PyQt6.QtGui import QFont, QBrush, QColor
import re
from animations import switch_widget, shake_window
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


class CareerExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Career Explorer")
        self.resize(1500, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Main container
        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        # create widgets once
        self.login_widget = login_window(self, "login")
        self.register_widget = login_window(self, "register")
        # create dashboard without username for now
        self.dashboard_widget = DashboardWidget(self, "")  

        # add to container layout and show only login initially
        self.container_layout.addWidget(self.login_widget)
        self.container_layout.addWidget(self.register_widget)
        self.container_layout.addWidget(self.dashboard_widget)
        self.register_widget.hide()
        self.dashboard_widget.hide()

        # connect signals once
        self.login_widget.login_btn.clicked.connect(self.login)
        self.login_widget.reg_btn.clicked.connect(self.show_register)
        self.register_widget.Sign_in.clicked.connect(self.validate)
        self.register_widget.go_back_btn.clicked.connect(self.show_login)

        # make sure dashboard logout works every time
        try:
            self.dashboard_widget.log_out.clicked.connect(self.show_login)
        except Exception:
            pass

        self.wrapper = QWidget(self)
        self.wrapper_layout = QVBoxLayout(self.wrapper)
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.wrapper_layout.addWidget(self.container)
        self.setCentralWidget(self.wrapper)

        self.overlay = PlayfulSplash(self)
        self.overlay.show()

    def switch_to(self, from_widget, to_widget, direction="left"):
        """
        Use your existing switch_widget if available to keep animations.
        Falls back to show/hide if switch_widget isn't available.
        """
        try:
            switch_widget(self, from_widget, to_widget, direction=direction)
        except Exception:
            from_widget.hide()
            to_widget.show()

    def show_login(self):
        try:
            self.login_widget.login_input.clear()
            self.login_widget.password_input.clear()
        except Exception:
            pass

        if self.dashboard_widget.isVisible():
            self.switch_to(self.dashboard_widget, self.login_widget, direction="down")
        elif self.register_widget.isVisible():
            self.switch_to(self.register_widget, self.login_widget, direction="right")
        else:
            self.login_widget.show()
            self.register_widget.hide()
            self.dashboard_widget.hide()

    def show_register(self):
        if self.login_widget.isVisible():
            self.switch_to(self.login_widget, self.register_widget, direction="left")
        else:
            self.register_widget.show()
            self.login_widget.hide()
            self.dashboard_widget.hide()

    def show_dashboard(self, username):
        if self.login_widget.isVisible():
            self.switch_to(self.login_widget, self.dashboard_widget, direction="up")

        else:
            self.login_widget.hide()
            self.register_widget.hide()
            self.dashboard_widget.show()
            
        if hasattr(self.dashboard_widget, "user_name"):
            self.dashboard_widget.user_name.setText(username)
        else:
            self.dashboard_widget.username = username

        try:
            try:
                self.dashboard_widget.log_out.clicked.disconnect()
            except Exception:
                pass
            self.dashboard_widget.log_out.clicked.connect(self.show_login)
        except Exception:
            pass

        from dashboard_handler import populate_recent_data
        recent_data = [
            {
                "name": "Juan Dela Cruz",
                "date": "2025-10-15",
                "specialized_course": "Web Dev",
                "specialized_course_pct": 85,
                "specialized_job": "Frontend Dev",
                "specialized_job_pct": 90
            },
        ]

        populate_recent_data(
            self.dashboard_widget.recent_container,
            recent_data,
            on_click=self.onclick
        )

    def functions_dashboard(self, username):
        self.show_dashboard(username)
        

    def onclick(self, recent_data):
        print("Clicked card:", recent_data)

    def login(self):
        from data_handler import get_all_users, binary_search_user
        username = self.login_widget.login_input.text().strip()
        password = self.login_widget.password_input.text().strip()

        if not username or not password:
            self.login_widget.error_message.setText("Please fill up everything.")
            self.login_widget.error_message.setStyleSheet("color: red; font-weight: bold;")
            shake_window(self)
            return

        users = get_all_users()
        user = binary_search_user(users, username)

        if user and user["password"] == password:
            print("Login successful!")
            self.show_dashboard(username)
        else:
            self.login_widget.error_message.setText("Invalid credentials. Please try again.")
            self.login_widget.error_message.setStyleSheet("color: red; font-weight: bold;")
            shake_window(self)

    def validate(self):
        from data_handler import save_user
        email = self.register_widget.rEmail_input.text().strip()
        password = self.register_widget.rPass_input.text().strip()
        username = self.register_widget.rUser_input.text().strip()

        def show_error(message):
            self.register_widget.error_message.setText(message)
            self.register_widget.error_message.setStyleSheet("color: red; font-weight: bold;")
            shake_window(self)

        if not email or not password or not username:
            show_error("Please fill up everything.")
            return

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if not re.match(pattern, password):
            show_error("Password must be 8+ chars, upper, lower, number & symbol.")
            return

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            show_error("Please enter a valid email address.")
            return

        self.register_widget.error_message.setText("Registration successful!")
        self.register_widget.error_message.setStyleSheet("color: green; font-weight: bold;")
        user_id = save_user(username, password, email)
        print(f"User saved with ID {user_id}")
