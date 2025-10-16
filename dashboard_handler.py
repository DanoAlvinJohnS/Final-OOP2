from data_card import DataCard

def clear_layout(layout):
    while layout.count():
        it = layout.takeAt(0)
        w = it.widget()
        if w:
            w.deleteLater()

def populate_recent_data(container_layout, recent_data, on_click=None):
    clear_layout(container_layout)
    container_layout.setContentsMargins(20, 20, 20, 20)
    container_layout.setSpacing(20)

    parent_width = container_layout.parentWidget().width() if container_layout.parentWidget() else 1000

    for item in recent_data:
        card = DataCard(item, parent_width=parent_width, on_click=on_click)
        container_layout.addWidget(card)

    container_layout.addStretch()
