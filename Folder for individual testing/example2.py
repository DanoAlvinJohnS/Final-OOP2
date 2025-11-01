import pandas as pd
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt

class DetailedPopup(QWidget):
    def __init__(self, username, specialization, job):
        super().__init__()
        self.setWindowTitle("Detailed Job Information")
        self.resize(480, 400)

        # QLabel (for HTML-based display)
        self.detailed = QLabel()
        self.detailed.setWordWrap(True)
        self.detailed.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detailed.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border-radius: 10px;
                padding: 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.detailed)

        # Load and display job details
        self.load_detailed_info(username, specialization, job)

    def load_detailed_info(self, username, specialization, job):
        """Loads job info from CSV and formats it nicely in HTML."""
        csv_path = "sources/datasets/job_specializations.csv"
        df = pd.read_csv(csv_path)

        # Filter data
        filtered = df[(df["specialization"] == specialization) & (df["job"] == job)]

        if filtered.empty:
            self.detailed.setText("<b style='color:red;'>No data found for this job.</b>")
            return

        # Sort by weight descending
        filtered = filtered.sort_values(by="weight", ascending=False)
        top_factor = filtered.iloc[0]

        # Build HTML
        html = f"""
        <div style="line-height:1.6;">
            <b style="color:#2196F3;">Username:</b> {username}<br>
            <b style="color:#2196F3;">Specialization:</b> {specialization}<br>
            <b style="color:#2196F3;">Job:</b> {job}<br><br>
            <b>Key Factors:</b><br>
        """

        # Append each factor (highlight highest)
        for _, row in filtered.iterrows():
            name = row["code_or_trait"]
            weight = row["weight"] * 100
            color = "#FFD700" if row["code_or_trait"] == top_factor["code_or_trait"] else "#FFFFFF"
            html += f"• <span style='color:{color};'>{name}</span> — <b>{weight:.0f}%</b><br>"

        html += "</div>"
        self.detailed.setText(html)


if __name__ == "__main__":
    app = QApplication([])

    # Example usage
    popup = DetailedPopup(username="John Doe",
                          specialization="Hardware & Embedded Systems",
                          job="Embedded Systems Engineer")
    popup.show()

    app.exec()
