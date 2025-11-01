from PyQt6.QtWidgets import QTreeWidgetItem, QMessageBox, QLabel, QVBoxLayout, QHeaderView, QSizePolicy
from ui_handler.animations import FancyCircularProgress
from PyQt6.QtCore import Qt
import pandas as pd
import os

OUTPUT_FOLDER = "sources/results"
import re
import calendar

last_results = {}  # { specialization_name: previous_compatibility }

def format_filename_to_date(filename: str) -> str:

    match = re.search(r"(\d{1,2})_(\d{1,2})_(\d+)\.xlsx$", filename)
    if not match:
        return f"No 0."

    month_num, day, number = map(int, match.groups())

    # Convert month number to abbreviation
    if 1 <= month_num <= 12:
        month_name = calendar.month_abbr[month_num]
    else:
        month_name = "Unknown"

    return f"No. {number}, {month_name} {day}"

def update_top5_table(dashboard, df_sorted, score_col="Compatibility"):
    from PyQt6.QtWidgets import QTableWidgetItem
    from PyQt6.QtGui import QColor, QBrush, QFont

    if not hasattr(dashboard, "top5_table") or dashboard.top5_table is None:
        print("[WARN] top5_table not found in dashboard.")
        return
    
    table = dashboard.top5_table
    table.clear()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["Job", "Score (%)"])
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    top5 = df_sorted.head(5)
    table.setRowCount(len(top5))

    for i, (_, row) in enumerate(top5.iterrows()):
        job = str(row.get("Job", row.get("job", "Unknown Job")))
        score = row.get(score_col, 0.0)

        # Create table items
        job_item = QTableWidgetItem(job)
        score_item = QTableWidgetItem(f"{score:.2f}")

        if i == 0:
            score_item.setForeground(QBrush(QColor("#FFD700")))
            job_item.setForeground(QBrush(QColor("#FFD700")))
            job_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            score_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        table.setItem(i, 0, job_item)
        table.setItem(i, 1, score_item)

    table.resizeColumnsToContents()
    table.setAlternatingRowColors(True)
    table.setEditTriggers(table.EditTrigger.NoEditTriggers)
    table.setSelectionMode(table.SelectionMode.NoSelection)
    table.horizontalHeader().setStretchLastSection(True)

def on_file_selected(dashboard, item, username):
    import pandas as pd, os, re, calendar
    from PyQt6.QtWidgets import QLabel, QVBoxLayout, QMessageBox
    from PyQt6.QtCore import Qt
    from ui_handler.animations import FancyCircularProgress

    def format_filename_to_date(filename: str) -> str:
        match = re.search(r"(\d{1,2})_(\d{1,2})_(\d+)\.xlsx$", filename)
        if not match:
            return f"Unknown ({filename})"
        month_num, day, number = map(int, match.groups())
        month_name = calendar.month_abbr[month_num] if 1 <= month_num <= 12 else "Unknown"
        return f"No. {number}, {month_name} {day}"

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

        # Determine score column
        if "Compatibility" in df.columns:
            score_col = "Compatibility"
        elif "compatibility" in df.columns:
            score_col = "compatibility"
        else:
            score_col = numeric_cols[0]

        df_sorted = df.sort_values(by=score_col, ascending=False).reset_index(drop=True)
        max_val = df_sorted[score_col].max()
        update_top5_table(dashboard, df_sorted, score_col)
        row = df_sorted.iloc[0]

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

        specialization_name = spec_name or "Unknown"
        job_name = job_name or "Unknown"

        previous_val = dashboard.last_results.get(specialization_name, None)
        change = None
        if previous_val is not None:
            change = max_val - previous_val
        dashboard.last_results[specialization_name] = max_val

        if max_val >= 70:
            recommendation = "Excellent match — pursue this field!"
        elif max_val >= 50:
            recommendation = "Moderate match — explore further training or projects."
        elif max_val >= 30:
            recommendation = "Low match — consider developing related skills."
        else:
            recommendation = "Weak match — try exploring a different specialization."

        # Trend text
        if change is not None:
            trend_symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
            trend_text = f"{trend_symbol} {abs(change):.2f}% vs last"
        else:
            trend_text = "— first record —"

        formatted_date = format_filename_to_date(os.path.basename(file_path))
        if hasattr(dashboard, "viewing_l") and dashboard.viewing_l is not None:
            dashboard.viewing_l.setText(f"Currently viewing: {formatted_date}")
        else:
            print("[WARN] viewing_l label not found in dashboard UI.")

        detailed_path = os.path.join("sources", "datasets", "job_specializations.csv")
        csv_factors = []
        if os.path.exists(detailed_path):
            details_df = pd.read_csv(detailed_path)
            job_data = details_df[
                (details_df["specialization"].str.lower() == specialization_name.lower()) &
                (details_df["job"].str.lower() == job_name.lower())
            ]
            if not job_data.empty:
                job_data = job_data.sort_values(by="weight", ascending=False)
                top_factor = job_data.iloc[0]["code_or_trait"]
                for _, r in job_data.iterrows():
                    csv_factors.append((r["code_or_trait"], r["weight"], r["code_or_trait"] == top_factor))
        else:
            print(f"[WARN] job_specializations.csv not found at {detailed_path}")

        detailed_html = f"""
        <div style="
            background-color: white;
            color: black;
            font: 700 11pt 'Arial';
            border: 1px solid rgb(180, 180, 180);
            border-radius: 20px;
            padding: 6px 12px;
        ">
            <p><span style='color:blue; font-weight:bold;'>Username:</span> {username}</p>
            <p><span style='color:blue; font-weight:bold;'>Specialization:</span> {specialization_name}</p>
            <p><span style='color:blue; font-weight:bold;'>Job:</span> {job_name}</p>
            <p><b>Compatibility:</b> {max_val:.2f}% ({trend_text})</p>
            <p><b>Recommendation:</b> {recommendation}</p>
            <hr>
            <p><b>Key Factors:</b></p>
        """

        if csv_factors:
            for code, weight, is_top in csv_factors:
                percent = weight * 100 if weight <= 1 else weight  
                color = "#FFD700" if is_top else "#333333"
                detailed_html += f"<p style='color:{color};'>• {code}: {percent:.2f}</p>"
        else:
            detailed_html += "<p>No key factors found in CSV.</p>"

        detailed_html += "</div>"

        if not hasattr(dashboard, "detailed") or dashboard.detailed is None:
            dashboard.detailed = QLabel()
            dashboard.detailed.setWordWrap(True)
            dashboard.detailed.setAlignment(Qt.AlignmentFlag.AlignTop)
            if dashboard.compat_frame.layout() is None:
                dashboard.compat_frame.setLayout(QVBoxLayout())
            dashboard.compat_frame.layout().addWidget(dashboard.detailed)

        dashboard.detailed.setText(detailed_html)

        if dashboard.compat_frame.layout() is None:
            dashboard.compat_frame.setLayout(QVBoxLayout())
        layout = dashboard.compat_frame.layout()
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w and isinstance(w, FancyCircularProgress):
                w.deleteLater()

        progress = FancyCircularProgress()
        layout.insertWidget(0, progress, alignment=Qt.AlignmentFlag.AlignCenter)
        progress.setTargetValue(max_val)

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
        
        msg = f"{file_name}\n\nHighest Specialization:\n{specialization}, {specialization_score:.2f}%"
        if job:
            msg += f"\n\nHighest Job Match:\n{job}, {job_score:.2f}%"

        QMessageBox.information(None, "File Summary", msg)

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to open {file_name}\n\n{str(e)}")
