import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence
def kill_everything(confirm=True, fade=True, duration=600):
    """
    Universal kill switch with optional fade-out animation.
    Works anywhere in your PyQt6 app.
    """
    app = QApplication.instance()
    if app is None:
        print("[KILL SWITCH] No QApplication instance found.")
        sys.exit(0)

    if confirm:
        reply = QMessageBox.question(
            None,
            "Exit Confirmation",
            "Are you sure you want to close everything?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            print("[KILL SWITCH] Cancelled by user.")
            return

    widgets = QApplication.topLevelWidgets()
    print(f"[KILL SWITCH] Closing {len(widgets)} open windows...")

    if fade:
        for widget in widgets:
            try:
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                anim = QPropertyAnimation(effect, b"opacity")
                anim.setDuration(duration)
                anim.setStartValue(1)
                anim.setEndValue(0)
                anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                anim.start()
            except Exception as e:
                print(f"[WARN] Failed to animate fade for {widget}: {e}")

        # delay quit until animation done
        QTimer.singleShot(duration + 100, lambda: _final_kill(app, widgets))
    else:
        _final_kill(app, widgets)

def _final_kill(app, widgets):
    for widget in widgets:
        try:
            widget.close()
        except Exception as e:
            print(f"[WARN] Failed to close {widget}: {e}")
    app.quit()
    sys.exit(0)

def minimize_all():
    """
    Minimizes all open windows in the current PyQt6 application.
    Works globally.
    """
    app = QApplication.instance()
    if app is None:
        print("[MINIMIZE] No QApplication instance found.")
        return

    widgets = QApplication.topLevelWidgets()
    print(f"[MINIMIZE] Minimizing {len(widgets)} open windows...")

    for widget in widgets:
        try:
            widget.showMinimized()
        except Exception as e:
            print(f"[WARN] Could not minimize {widget}: {e}")



def bind_global_shortcuts(window):
    """
    Adds Ctrl+Q (Exit) and Ctrl+M (Minimize) shortcuts to any window.
    Works for dashboard, login, register, etc.
    """
    QShortcut(QKeySequence("Ctrl+Q"), window, activated=kill_everything)
    QShortcut(QKeySequence("Ctrl+M"), window, activated=minimize_all)
    print(f"[SHORTCUTS] Bound Ctrl+Q and Ctrl+M for {type(window).__name__}")
