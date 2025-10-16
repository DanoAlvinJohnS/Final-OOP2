from PyQt6.QtWidgets import (
    QApplication, QWidget, QGraphicsView,
    QGraphicsScene, QGraphicsTextItem, QGraphicsOpacityEffect, QVBoxLayout
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPointF, QRandomGenerator, Qt
from PyQt6.QtGui import QFont


class ShapeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)

        # 🪟 Create the scene and view
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(self.view.renderHints())
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent; border: none;")

        # 🧭 Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

        # 📏 Scene rectangle matches widget
        self.scene.setSceneRect(0, 0, self.width(), self.height())

        self.shape_anims = []

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # keep scene size in sync with widget size
        self.scene.setSceneRect(0, 0, self.width(), self.height())

    def spawn_shapes(self, count: int = 30):
        center = self.scene.sceneRect().center()
        texts = ["X", "O", "☐"]

        for i in range(count):
            text = texts[i % len(texts)]

            # 🟡 Shape
            shape = QGraphicsTextItem(text)
            shape.setDefaultTextColor(Qt.GlobalColor.white)
            shape.setFont(QFont("Arial", 30))
            shape.setPos(center - QPointF(shape.boundingRect().width() / 2,
                                          shape.boundingRect().height() / 2))
            shape.setScale(0.1)
            self.scene.addItem(shape)

            # 📈 Scale
            scale_anim = QPropertyAnimation(shape, b"scale")
            scale_anim.setDuration(500)
            scale_anim.setStartValue(0.1)
            scale_anim.setEndValue(0.8)
            scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

            # 🪁 Move (clamped to widget boundaries)
            max_x = self.scene.width() - shape.boundingRect().width()
            max_y = self.scene.height() - shape.boundingRect().height()
            end_x = QRandomGenerator.global_().bounded(0, int(max_x))
            end_y = QRandomGenerator.global_().bounded(0, int(max_y))

            move_anim = QPropertyAnimation(shape, b"pos")
            move_anim.setDuration(3000)
            move_anim.setStartValue(shape.pos())
            move_anim.setEndValue(QPointF(end_x, end_y))
            move_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            # 🌫 Fade
            effect = QGraphicsOpacityEffect()
            shape.setGraphicsEffect(effect)
            fade_anim = QPropertyAnimation(effect, b"opacity")
            fade_anim.setDuration(2000)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)

            # 🌀 Rotation
            rot_anim = QPropertyAnimation(shape, b"rotation")
            rot_anim.setDuration(1500)
            rot_anim.setStartValue(0)
            rot_anim.setEndValue(QRandomGenerator.global_().bounded(-180, 180))
            rot_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            anim_group = (scale_anim, move_anim, fade_anim, rot_anim)
            self.shape_anims.append(anim_group)

            # 🧹 Cleanup
            def on_fade_finished(shape=shape, anims=anim_group):
                if shape.scene():
                    self.scene.removeItem(shape)
                if anims in self.shape_anims:
                    self.shape_anims.remove(anims)

            fade_anim.finished.connect(on_fade_finished)

            # ▶ Start
            scale_anim.start()
            move_anim.start()
            fade_anim.start()
            rot_anim.start()


if __name__ == "__main__":
    app = QApplication([])
    w = ShapeWidget()
    w.show()
    w.spawn_shapes(30)
    app.exec()
