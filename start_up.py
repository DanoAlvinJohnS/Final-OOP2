import re
import os
import pandas as pd
from datetime import datetime

from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtWidgets import ( QMainWindow, QWidget, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt

from dashboard_gui import login_window, DashboardWidget
from dashboard_handler import populate_recent_data
from data_card import RecentDataPopup
from inputgui import input_window
from ui_handler.animations import switch_widget, shake_window, PlayfulSplash
from ui_handler.statistic_handler import load_all_structure
from ui_handler.system_control import kill_everything, minimize_all, bind_global_shortcuts


class CareerExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Career Explorer")
        self.resize(1500, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.generated_file_path = None
        
        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        self.login_widget = login_window(self, "login")
        self.register_widget = login_window(self, "register")

        self.dashboard_widget = DashboardWidget(self, "")  

        self.container_layout.addWidget(self.login_widget)
        self.container_layout.addWidget(self.register_widget)
        self.container_layout.addWidget(self.dashboard_widget)
        self.register_widget.hide()
        self.dashboard_widget.hide()

        self.login_widget.login_btn.clicked.connect(self.login)
        self.login_widget.reg_btn.clicked.connect(self.show_register)
        self.register_widget.Sign_in.clicked.connect(self.validate)
        self.register_widget.go_back_btn.clicked.connect(self.show_login)

        bind_global_shortcuts(self.dashboard_widget)
        bind_global_shortcuts(self.login_widget)
        bind_global_shortcuts(self.register_widget)
        
        self.dashboard_widget.exit_h.clicked.connect(kill_everything)
        self.dashboard_widget.min_h.clicked.connect(minimize_all)
        self.dashboard_widget.exit_r.clicked.connect(kill_everything)
        self.dashboard_widget.min_r.clicked.connect(minimize_all)
        self.dashboard_widget.exit_s.clicked.connect(kill_everything)
        self.dashboard_widget.min_s.clicked.connect(minimize_all)

        self.login_widget.exit_log.clicked.connect(kill_everything)
        self.login_widget.min_log.clicked.connect(minimize_all)
        
        self.register_widget.exit_reg.clicked.connect(kill_everything)
        self.register_widget.min_reg.clicked.connect(minimize_all)

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
            self.clear_recent_data()
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
        self.current_username = username
        self.dashboard_widget.username = username
        self.dashboard_widget.mainStackWig.currentChanged.connect(self.on_page_changed)

        if self.login_widget.isVisible():
            self.switch_to(self.login_widget, self.dashboard_widget, direction="up")
        else:
            self.login_widget.hide()
            self.register_widget.hide()
            self.dashboard_widget.show()
        self.dashboard_widget.last_results = {}  
        load_all_structure(self.dashboard_widget, username)
        
        if hasattr(self.dashboard_widget, "user_name"):
            self.dashboard_widget.user_name.setText(username)
        
        try:
            self.dashboard_widget.generate_data.clicked.disconnect()
        except Exception:
            pass

        self.dashboard_widget.generate_data.clicked.connect(
            lambda: self.input_data(self.dashboard_widget.username)
        )

        try:
            self.dashboard_widget.view_graph.clicked.disconnect()
        except Exception:
            pass

        self.dashboard_widget.view_graph.clicked.connect(
            lambda: self.show_page_create_with_data(self.generated_file_path)
            if self.generated_file_path
            else QMessageBox.warning(None, "No Data", "Please generate or input data first.")
        )
        self.load_recent_data(username)
        
    def input_data(self, username):
        file_path = input_window(username)
        if file_path:
            self.generated_file_path = file_path
            print(f"[OK] File generated at: {self.generated_file_path}")

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText("Accepted!")
            msg.exec()

            self.refresh_recent_data(username)
        else:
            print("[INFO] Input canceled or no file generated.")

    def load_recent_data(self, username):

        user_folder = f"sources/results/{username}"
        if not os.path.exists(user_folder):
            print(f"[WARN] No results folder found for {username}.")
            return

        # Find Excel files
        files = [f for f in os.listdir(user_folder) if f.endswith(".xlsx")]
        if not files:
            print(f"[WARN] No result files found for {username}.")
            return

        # Sort files by modified time (newest first)
        files.sort(key=lambda f: os.path.getmtime(os.path.join(user_folder, f)), reverse=True)
        files = files[:5]

        recent_data = []
        for f in files:
            file_path = os.path.join(user_folder, f)
            try:
                df = pd.read_excel(file_path)

                # Ensure necessary columns exist
                if not all(col in df.columns for col in ["specialization", "job", "compatibility_percent"]):
                    print(f"[SKIP] Missing columns in {f}")
                    continue

                # Pick top row
                top_row = df.sort_values("compatibility_percent", ascending=False).iloc[0]

                recent_data.append({
                    "name": username,
                    "date": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d"),
                    "specialized_course": str(top_row.get("specialization", "N/A")),
                    "specialized_course_pct": round(float(top_row.get("compatibility_percent", 0)), 2),
                    "specialized_job": str(top_row.get("job", "N/A")),
                    "specialized_job_pct": round(float(top_row.get("compatibility_percent", 0)), 2),
                    "file_path": file_path,
                })

            except Exception as e:
                print(f"[ERROR] Failed to load {f}: {e}")

        if hasattr(self.dashboard_widget, "recent_container"):
            layout = self.dashboard_widget.recent_container.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            print("[OK] Cleared previous recent data.")

        if recent_data:
            populate_recent_data(
                container_layout=self.dashboard_widget.recent_container,
                recent_data=recent_data,
                on_click=lambda data: self.onclick(data, username)
            )
            print(f"[OK] Loaded {len(recent_data)} recent result(s) for {username}.")
        else:
            print(f"[INFO] No valid result data to display for {username}.")

    
    def clear_recent_data(self):
        try:
            if hasattr(self.dashboard_widget, "recent_container"):
                layout = self.dashboard_widget.recent_container.layout()
                if layout:
                    while layout.count():
                        item = layout.takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.deleteLater()
                print("[OK] Cleared recent data from dashboard.")
            else:
                print("[WARN] No recent_container found in dashboard_widget.")
        except Exception as e:
            print(f"[ERROR] Failed to clear recent data: {e}")

            
    def onclick(self, recent_data, username):
        def handle_remove(data):
            file_path = data.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"[OK] Removed file: {file_path}")
                    QMessageBox.information(None, "Removed", "Data file has been deleted.")
                except Exception as e:
                    QMessageBox.warning(None, "Error", f"Could not delete file:\n{e}")
            else:
                QMessageBox.warning(None, "Not Found", "File not found or already deleted.")    

        self.popup = RecentDataPopup(
            recent_data,
            on_view=lambda data, path: self.show_page_create_with_data(path),
            on_remove=handle_remove,
            refresh_callback=lambda: self.refresh_recent_data(username)
        )

        self.popup.show()

    def on_page_changed(self, index):
        try:
            current_page = self.dashboard_widget.mainStackWig.widget(index)
            page_name = current_page.objectName()

            pages_to_refresh = ["pageHome", "pageCreate", "pageStatistic"]

            if page_name in pages_to_refresh:
                username = getattr(self, "current_username", None)
                if username:
                    print(f"[REFRESH] Switched to {page_name} | reloading recent data for {username}")
                    self.refresh_recent_data(username)
                else:
                    print("[WARNING] No username found | cannot refresh data.")
        except Exception as e:
            print(f"[ERROR] on_page_changed failed: {e}")

            
    def show_page_create_with_data(self, file_path):
        try:
            self.dashboard_widget.mainStackWig.setCurrentWidget(self.dashboard_widget.pageCreate)
            print(f"[OK] Switched to pageCreate for file: {file_path}")
 
            page = self.dashboard_widget.pageCreate

            predicting_container = page.findChild(QWidget, "predicting_widget")

            if predicting_container is None:
                raise AttributeError("[ERROR on UI] | predicting_widget not found in pageCreate")

            if hasattr(page, "predicting_widget_instance") and page.predicting_widget_instance is not None:
                print("[INFO] Reusing existing PredictingWidget instance.")
                page.predicting_widget_instance.load_file(file_path)
            else:
                print("[INFO] Creating new PredictingWidget inside predicting_widget container...")
                from visual import PredictingWidget
                predicting_widget = PredictingWidget(file_path)

                layout = predicting_container.layout()
                if layout is None:
                    layout = QVBoxLayout(predicting_container)
                    predicting_container.setLayout(layout)
                else:
                    while layout.count():
                        item = layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()

                layout.addWidget(predicting_widget)
                page.predicting_widget_instance = predicting_widget

            print("[OK] Loaded data into predicting_widget container.")

        except Exception as e:
            print(f"[ERROR] Failed to load data in pageCreate.predicting_widget: {e}")

    def refresh_recent_data(self, username):
        self.clear_recent_data()
        self.load_recent_data(username)
        load_all_structure(self.dashboard_widget, username)
       

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
