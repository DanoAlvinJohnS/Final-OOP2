import os
from PyQt6.QtWidgets import QListWidgetItem

class StatisticHandler:
    def __init__(self, dashboard, username):
        """
        Handles file listing and selection for the Statistics page.
        """
        self.dashboard = dashboard
        self.username = username
        self.page = self.dashboard.pageStatistic

        self.setup_connections()

    # -------------------------------
    # Connect Events
    # -------------------------------
    def setup_connections(self):
        """Connect widget signals."""
        try:
            self.page.listFiles.itemClicked.connect(self.on_file_selected)
            print("[OK] Connected Statistic page signals.")
        except Exception as e:
            print(f"[ERROR] Failed to connect signals: {e}")

    # -------------------------------
    # Load Result Files
    # -------------------------------
    def load_result_files(self):
        """Loads all result files from sources/results/<username>/"""
        folder_path = os.path.join("sources", "results", self.username)
        self.page.listFiles.clear()

        if not os.path.exists(folder_path):
            print(f"[INFO] No results folder found for '{self.username}'.")
            return

        files = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        if not files:
            print(f"[INFO] No result files found in {folder_path}")
            return

        for file_name in files:
            self.page.listFiles.addItem(QListWidgetItem(file_name))

        print(f"[OK] Loaded {len(files)} result file(s) for user '{self.username}'.")

    # -------------------------------
    # File Selection
    # -------------------------------
    def on_file_selected(self, item):
        """Triggered when a file is clicked in the listFiles widget."""
        file_name = item.text()
        file_path = os.path.join("sources", "results", self.username, file_name)

        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # show the file content in fileViewer widget
            self.page.fileViewer.setPlainText(content)
            print(f"[OK] Loaded file content: {file_name}")

        except Exception as e:
            print(f"[ERROR] Failed to open '{file_name}': {e}")
