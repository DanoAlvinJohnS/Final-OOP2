from PyQt6.QtWidgets import QTreeWidgetItem, QMessageBox, QLabel, QVBoxLayout
from ui_handler.animations import FancyCircularProgress
from PyQt6.QtCore import Qt
import pandas as pd
import os

OUTPUT_FOLDER = "sources/results"
import re
import calendar

last_results = {}  

def format_filename_to_date(filename: str) -> str:
    match = re.search(r"(\d{1,2})_(\d{1,2})_(\d+)\.xlsx$", filename)
    if not match:
        return f"No 0."

    month_num, day, number = map(int, match.groups())

    if 1 <= month_num <= 12:
        month_name = calendar.month_abbr[month_num]
    else:
        month_name = "Unknown"

    return f"No. {number}, {month_name} {day}"


def on_file_selected(dashboard, item, username):
    file_path = item.data(0, 1000)
    if not file_path or not os.path.exists(file_path):
        print(f"[ERROR] File missing: {file_path}")
        return

    try:
        df = pd.read_excel(file_path)

        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        if len(numeric_cols) == 0:
            QMessageBox.warning(dashboard, "No Data", "No numeric columns found in this file.")
            return

        if "Compatibility" in df.columns:
            max_val = df["Compatibility"].max()
            row = df.loc[df["Compatibility"].idxmax()]
        else:
            avg_series = df[numeric_cols].mean(axis=1)
            max_idx = avg_series.idxmax()
            max_val = avg_series[max_idx]
            row = df.iloc[max_idx]

        # Detect Job & Specialization
        job_name = None
        spec_name = None

        for col in ["Job", "job", "Position", "Role", "Occupation"]:
            if col in df.columns:
                job_name = row[col]
                break

        for col in ["Specialization", "specialization", "Field", "Track"]:
            if col in df.columns:
                spec_name = row[col]
                break

        # Prepare display text
        display_lines = []
        if job_name:
            display_lines.append(f"Job: {job_name}")
        if spec_name:
            display_lines.append(f"Specialization: {spec_name}")
        display_lines.append(f"{max_val:.2f}%")

        display_text = "\n".join(display_lines)
        max_val = min(max_val, 100)

        specialization_name = row["specialization"] if "specialization" in df.columns else "Unknown"
        job_name = row["job"] if "job" in df.columns else "Unknown"

        # Compute change (trend)
        previous_val = dashboard.last_results.get(specialization_name, None)
        change = None
        if previous_val is not None:
            change = max_val - previous_val

        # Update record
        dashboard.last_results[specialization_name] = max_val

        if max_val >= 70:
            recommendation = "Excellent match — pursue this field!"
        elif max_val >= 50:
            recommendation = "Moderate match — explore further training or projects."
        elif max_val >= 30:
            recommendation = "Low match — consider developing related skills."
        else:
            recommendation = "Weak match — try exploring a different specialization."
        
        if change is not None:
            trend_symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
            trend_text = f"{trend_symbol} {abs(change):.2f}% vs last"
        else:
            trend_text = "— first record —"
        formatted_date = format_filename_to_date(os.path.basename(file_path))
        dashboard.label_4.setText(f"{specialization_name}\n{job_name}\n{max_val:.2f}% ({trend_text}\nRecommendation: {recommendation})")
        dashboard.viewing_l.setText(f'Currently viewing: {formatted_date}')
        # Prepare frame layout
        if dashboard.compat_frame.layout() is None:
            dashboard.compat_frame.setLayout(QVBoxLayout())
        layout = dashboard.compat_frame.layout()

        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        progress = FancyCircularProgress()
        label = QLabel(display_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1a1a1a;
                margin-top: 10px;
            }
        """)

        layout.addWidget(progress, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        progress.setTargetValue(max_val)
        
        # --- Custom log output ---
        formatted_date = format_filename_to_date(os.path.basename(file_path))
        print(f"[OK] {formatted_date} | Displayed compatibility: {max_val:.2f}% "
              f"(Specialization: {spec_name or 'Unknown'}, Job: {job_name or 'Unknown'})")
    except Exception as e:
        QMessageBox.critical(dashboard, "Error", f"Failed to load {file_path}\n\n{e}")

def load_all_structure(dashboard, username):
    output_folder = os.path.join("sources/results", username)
    dashboard.track_list.clear()

    if not os.path.exists(output_folder):
        print("[INFO] No output folder found.")
        return

    files = [f for f in os.listdir(output_folder) if f.endswith(".xlsx")]
    if not files:
        print("[INFO] No .xlsx files found.")
        return

    for file in files:
        file_path = os.path.join(output_folder, file)
        display_name = format_filename_to_date(file) 
        item = QTreeWidgetItem([display_name])
        item.setData(0, 1000, file_path)
        dashboard.track_list.addTopLevelItem(item)

        
    dashboard.track_list.expandAll()
    dashboard.track_list.itemClicked.connect(lambda item, _: on_file_selected(dashboard, item, username))
    print(f"[OK] Loaded {len(files)} .xlsx file(s) into tree.")


def on_item_clicked(item, username):
    file_name = item.text(0)
    file_path = os.path.join("sources/results", username, file_name)

    if not os.path.exists(file_path):
        QMessageBox.warning(None, "File Missing", f"Cannot find file: {file_name}")
        return

    try:
        df = pd.read_excel(file_path)

        if "specialization" not in df.columns or "compatibility" not in df.columns:
            QMessageBox.warning(None, "Invalid File", f"{file_name} does not contain expected data.")
            return

        spec_row = df.loc[df["compatibility"].idxmax()]
        specialization = spec_row["specialization"]
        specialization_score = spec_row["compatibility"]

        job, job_score = None, None
        if "job" in df.columns and "job_compatibility" in df.columns:
            job_row = df.loc[df["job_compatibility"].idxmax()]
            job = job_row["job"]
            job_score = job_row["job_compatibility"]

        msg = f"📘 {file_name}\n\nHighest Specialization:\n{specialization}, {specialization_score:.2f}%"
        if job:
            msg += f"\n\nHighest Job Match:\n{job}, {job_score:.2f}%"

        QMessageBox.information(None, "File Summary", msg)

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to open {file_name}\n\n{str(e)}")
