import pandas as pd
import plotly.graph_objects as go
from PyQt6.QtWidgets import (
    QWidget, QComboBox, QLabel, QHBoxLayout, QGridLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class PredictingWidget(QWidget):
    def __init__(self, file_path=None):
        super().__init__()
        self.setWindowTitle("Job Specialization Chart")

        # === Main Grid Layout ===
        grid = QGridLayout()
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(15)

        # === Top controls layout ===
        control_layout = QHBoxLayout()

        # --- Specialization dropdown ---
        self.specialization_dropdown = QComboBox()
        self.specialization_dropdown.addItem("All Specializations")
        self.specialization_dropdown.currentIndexChanged.connect(self.update_chart)
        control_layout.addWidget(QLabel("Specialization:"))
        control_layout.addWidget(self.specialization_dropdown)

        # --- Job view dropdown (Top 5 default, All Jobs last) ---
        self.job_dropdown = QComboBox()
        self.job_dropdown.addItems(["Top 5 Jobs", "Top 10 Jobs", "All Jobs"])
        self.job_dropdown.setCurrentIndex(0)  # Default: Top 5 Jobs
        self.job_dropdown.currentIndexChanged.connect(self.update_chart)
        control_layout.addWidget(QLabel("View:"))
        control_layout.addWidget(self.job_dropdown)

        # --- Chart type dropdown ---
        self.chart_type_dropdown = QComboBox()
        self.chart_type_dropdown.addItems(["Pie Chart", "Bar Chart"])
        self.chart_type_dropdown.currentIndexChanged.connect(self.update_chart)
        control_layout.addWidget(QLabel("Chart Type:"))
        control_layout.addWidget(self.chart_type_dropdown)

        control_layout.addStretch()

        # --- Chart display ---
        self.browser = QWebEngineView()
        self.browser.setMinimumHeight(500)

        grid.addLayout(control_layout, 0, 0)
        grid.addWidget(self.browser, 1, 0)
        grid.setRowStretch(1, 10)

        self.setLayout(grid)

        # === Data initialization ===
        self.df = None
        if file_path:
            self.load_data(file_path)

    # === Load Excel data ===
    def load_data(self, file_path):
        try:
            self.df = pd.read_excel(file_path)
            print(f"[OK] Loaded dataset: {file_path}")
            self.populate_specializations()
            self.update_chart()
        except Exception as e:
            print(f"[ERROR] Failed to load Excel file: {e}")
            self.df = pd.DataFrame()

    def populate_specializations(self):
        """Populate specialization dropdown dynamically."""
        self.specialization_dropdown.blockSignals(True)
        self.specialization_dropdown.clear()
        self.specialization_dropdown.addItem("All Specializations")

        if not self.df.empty:
            specializations = sorted(self.df["specialization"].unique())
            for spec in specializations:
                self.specialization_dropdown.addItem(spec)

        self.specialization_dropdown.blockSignals(False)
        
    def load_file(self, file_path):
        """Public method to load prediction data into this widget."""
        self.load_data(file_path)

    def update_chart(self):
        """Refresh chart when filters or type change."""
        if self.df is None or self.df.empty:
            print("[WARN] No data loaded.")
            return

        specialization = self.specialization_dropdown.currentText()
        job_filter = self.job_dropdown.currentText()
        chart_type = self.chart_type_dropdown.currentText()

        if specialization == "All Specializations":
            df_filtered = self.df.copy()
        else:
            df_filtered = self.df[self.df["specialization"] == specialization]

        if chart_type == "Pie Chart":
            self.generate_pie_chart(df_filtered, job_filter, specialization)
        else:
            self.generate_bar_chart(df_filtered, job_filter, specialization)

    # === PIE CHART ===
    def generate_pie_chart(self, df, job_filter, specialization):
        df = df.sort_values(by="compatibility_percent", ascending=False)
        if job_filter == "Top 5 Jobs":
            df = df.head(5)
        elif job_filter == "Top 10 Jobs":
            df = df.head(10)

        hover_texts = [
            f"<b>{row['job']}</b><br>{row['specialization']}<br>{row['compatibility_percent']}%"
            for _, row in df.iterrows()
        ]

        fig = go.Figure(data=[
            go.Pie(
                labels=df["job"],
                values=df["compatibility_percent"],
                hoverinfo="text",
                hovertext=hover_texts,
                textinfo="label+percent",
                marker=dict(line=dict(color="white", width=2)),
                hole=0.3
            )
        ])

        fig.update_layout(
            showlegend=False,
            margin=dict(t=70, b=60, l=60, r=60),
            height=600,
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        self.browser.setHtml(html)

    # === BAR CHART ===
    def generate_bar_chart(self, df, job_filter, specialization):
        df = df.sort_values(by="compatibility_percent", ascending=False)
        if job_filter == "Top 5 Jobs":
            df = df.head(5)
        elif job_filter == "Top 10 Jobs":
            df = df.head(10)

        colors = {
            "Software & Programming": "royalblue",
            "Networking & Cybersecurity": "firebrick",
            "Artificial Intelligence & Data": "darkorange",
            "Hardware & Embedded Systems": "seagreen",
            "Electronics & Signal Processing": "mediumslateblue",
            "Engineering Tools & Drafting": "darkcyan",
            "Industry & Field Work": "goldenrod",
            "Others": "gray"
        }

        bar_colors = [colors.get(spec, "lightgray") for spec in df["specialization"]]

        fig = go.Figure(
            data=[go.Bar(
                x=df["job"],
                y=df["compatibility_percent"],
                text=[f"{v:.1f}%" for v in df["compatibility_percent"]],
                textposition="auto",
                marker_color=bar_colors,
                hovertext=[
                    f"<b>{job}</b><br>{spec}<br>{v:.1f}%"
                    for job, spec, v in zip(df["job"], df["specialization"], df["compatibility_percent"])
                ],
                hoverinfo="text"
            )]
        )

        fig.update_layout(
            yaxis_title="Compatibility (%)",
            xaxis_title="Job Title",
            margin=dict(t=50, b=120, l=60, r=60),
            height=600,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_tickangle=-45,
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        self.browser.setHtml(html)
