# main_app_flashcard.py
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QStackedWidget,QStackedLayout,
    QLineEdit, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPixmap
from awd.data_model_flashcard import AppData
from awd.ui_styles_flashcard import (
    APP_STYLE, SIDEBAR_BUTTON_STYLE, HAMBURGER_STYLE,
    FONT_LARGE_BOLD, FONT_MEDIUM, FONT_BUTTON, FONT_LABEL,
    FONT_SUBTITLE, APP_STYLE_DARK, APP_STYLE_LIGHT, CREATE_FLASH, 
    MESSAGE_WARNING
)
#-------BAGONG LAGAY TO------
class FlipCard(QWidget):
    """Simple, fully working flip card — front/back toggle with fade."""
    def __init__(self, question, answer, bg_color="#FFFFFF", text_color="#333"):
        super().__init__()
        self.is_front = True

        # Create the front and back labels
        self.front = QLabel(question)
        self.back = QLabel(answer)

        for lbl in (self.front, self.back):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setWordWrap(True)
            lbl.setFont(QFont("Arial Rounded MT Bold", 14))
            lbl.setFixedSize(300, 180)
            lbl.setStyleSheet(f"""
                background-color: {bg_color};
                color: {text_color};
                border-radius: 20px;
                padding: 20px;
                border: 3px solid #aaa;
            """)

        # Stack both sides
        self.stack = QStackedLayout(self)
        self.stack.addWidget(self.front)
        self.stack.addWidget(self.back)
        self.stack.setCurrentWidget(self.front)

        # Connect click events
        self.front.mousePressEvent = self.flip
        self.back.mousePressEvent = self.flip

    def flip(self, event):
        """Instant flip (no fade) — guaranteed to show other side."""
        if self.is_front:
            self.stack.setCurrentWidget(self.back)
        else:
            self.stack.setCurrentWidget(self.front)
        self.is_front = not self.is_front

              
class FadeWidget(QWidget):
    def __init__(self, widget, parent_window):
        super().__init__()
        self.widget = widget
        self.parent_window = parent_window
        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.effect = QGraphicsOpacityEffect()
        self.widget.setGraphicsEffect(self.effect)
        self.anim = None

    def fade_in(self):
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def fade_out(self, next_widget):
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(lambda: self.switch_page(next_widget))
        self.anim.start()

    def switch_page(self, next_widget):
        next_widget.fade_in()
        self.parent_window.stacked.setCurrentWidget(next_widget)

class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.data = AppData()
        self.app = app
        self.apply_theme()
        
        self.setWindowTitle("Remora App Flow")
        self.setStyleSheet(APP_STYLE)
        self.setWindowIcon(QIcon("Icon.png"))
        
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.clicked.connect(self.toggle_btn)
        
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.theme_btn)
        
        self.stacked = QStackedWidget()
        
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.stacked)
        self.setLayout(layout)
        
        # Pages
        self.start_page = FadeWidget(self.create_start_page(), self)
        self.name_page = FadeWidget(self.create_name_page(), self)
        self.greet_page = FadeWidget(QLabel(alignment=Qt.AlignmentFlag.AlignCenter), self)
        self.greet_page.widget.setFont(FONT_MEDIUM)
        self.welcome_page = FadeWidget(self.create_welcome_page(), self)
        self.ask_page = FadeWidget(self.create_ask_page(), self)
        self.main_page = FadeWidget(self.create_main_page(), self)
        
        self.tutorial_page = FadeWidget(self.create_tutorial_page(), self)
        self.current_tutorial_step = 0  # track which tutorial slide we're on

        self.welcome_back_page = FadeWidget(QLabel(alignment=Qt.AlignmentFlag.AlignCenter), self)
        self.welcome_back_page.widget.setFont(FONT_MEDIUM)

        for page in [self.start_page, self.name_page, self.greet_page, self.welcome_page, self.ask_page, self.main_page]:
            self.stacked.addWidget(page)
            
        self.stacked.addWidget(self.tutorial_page)
        self.stacked.addWidget(self.welcome_back_page)

        # Connections
        self.start_btn.clicked.connect(lambda: self.start_page.fade_out(self.name_page))
        self.submit_name_btn.clicked.connect(self.show_greet)
        
        self.yes_btn.clicked.connect(self.show_tutorial)
        self.no_btn.clicked.connect(self.show_welcome_back)

        # Start page
        self.stacked.setCurrentWidget(self.start_page)
        self.start_page.fade_in()

        # Apply default theme
        self.apply_theme()
        
        # Topic pages
        
        #self.setup_topic_pages()
        
    

        
    def toggle_btn(self):
        """Switch between light and dark themes."""
        self.data.theme = "dark" if self.data.theme == "light" else "light"
        self.apply_theme()
        self.theme_btn.setText("☀️" if self.data.theme == "dark" else "🌙")

    def apply_theme(self):
        if self.data.theme == "dark":
            self.setStyleSheet(APP_STYLE_DARK)
        else:
            self.setStyleSheet(APP_STYLE_LIGHT)
            
        for page_name in [
            "main_page", "topics_page", "create_flashcard_page",
            "saved_flashcards_page", "existing_flashcard_page"
        ]:
            if hasattr(self, page_name):
                getattr(self, page_name).setStyleSheet(
                    APP_STYLE_DARK if self.data.theme == "dark" else APP_STYLE_LIGHT
                )
            
    def toggle_theme(self):
        if self.data.theme == "light":
            self.data.theme = "dark"
        else:
            self.data.theme = "light"
    
        self.apply_theme()

    def create_start_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = QPixmap("Icon.png")
        pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("READY WHEN YOU ARE!")
        subtitle.setFont(FONT_SUBTITLE)
        subtitle.setStyleSheet("color: #FC483D; letter-spacing: 2px; font-weight: 900;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.start_btn = QPushButton("BEGIN")
        self.start_btn.setFont(FONT_LARGE_BOLD)
        
        layout.addStretch()
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        return widget

    def create_name_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.name_label = QLabel("ENTER YOUR NAME")
        self.name_label.setFont(FONT_SUBTITLE)
        self.name_label.setStyleSheet("color: #434190")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Type it here...")
        
        self.name_input.repaint()
        self.name_input.setFont(FONT_SUBTITLE)
        
        self.submit_name_btn = QPushButton("Next")
        self.submit_name_btn.setFont(FONT_BUTTON)
        self.name_input.returnPressed.connect(self.show_greet)
        
        layout.addStretch()
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(self.submit_name_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        return widget

    def create_ask_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.ask_label = QLabel("New here?")
        self.ask_label.setFont(FONT_LABEL)
        self.ask_label.setStyleSheet("color: #434190")
        self.ask_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.yes_btn = QPushButton("Yes")
        self.no_btn = QPushButton("No")
        self.yes_btn.setFont(FONT_BUTTON)
        self.no_btn.setFont(FONT_BUTTON)
        layout.addStretch()
        layout.addWidget(self.ask_label)
        layout.addWidget(self.yes_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.no_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        return widget
    
    def create_tutorial_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
    
        self.tutorial_title = QLabel()
        self.tutorial_title.setFont(FONT_LARGE_BOLD)
        self.tutorial_title.setStyleSheet("color: #434190; font-weight: bold;")
        self.tutorial_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        self.tutorial_desc = QLabel()
        self.tutorial_desc.setFont(FONT_LABEL)
        self.tutorial_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tutorial_desc.setWordWrap(True)
        self.tutorial_desc.setStyleSheet("color: #555;")
    
        self.next_btn = QPushButton("Next ➜")
        self.next_btn.setFont(FONT_BUTTON)
        self.next_btn.clicked.connect(self.next_tutorial_step)
        
        self.skip_btn = QPushButton("Skip Tutorial ⏭️")
        self.skip_btn.setFont(FONT_BUTTON)
        self.skip_btn.clicked.connect(lambda: self.tutorial_page.fade_out(self.main_page))
        
        self.tutorial_desc.setStyleSheet("color: #555; padding: 0 40px;")
        
        layout.addStretch()
        layout.addWidget(self.tutorial_title)
        layout.addWidget(self.tutorial_desc)
        layout.addSpacing(20)
        layout.addWidget(self.next_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
    
        return widget

    def show_tutorial(self):
        self.current_tutorial_step = 0
        self.ask_page.fade_out(self.tutorial_page)
        self.update_tutorial_step()
        
    def update_tutorial_step(self):
        """Update tutorial content based on current step"""
        steps = [
            {
                "title": "Adding Flashcards",
                "desc": "Click the '+' button or 'Add Flashcard' in the main screen to create a new flashcard.\nYou can enter a question, an answer, and save it instantly."
            },
            {
                "title": "Navigating the App",
                "desc": "Use the sidebar ☰ to explore:\n🏠 Home – View your flashcards\n👤 Profile – Check your info\n⚙️ Settings – Customize your theme\n📊 Statistics – See your study progress."
            },
            {
                "title": "Using Existing Flashcards",
                "desc": "Select any flashcard to study. Flip the card to see the answer and mark if you got it right or wrong. Remora tracks your progress automatically!"
            }
        ]
    
        # Update content
        step = steps[self.current_tutorial_step]
        self.tutorial_title.setText(step["title"])
        self.tutorial_desc.setText(step["desc"])
    
        # Update button text
        if self.current_tutorial_step < len(steps) - 1:
            self.next_btn.setText("Next ➜")
        else:
            self.next_btn.setText("Finish ✅")

    def next_tutorial_step(self):
        """Handle next step or finish tutorial"""
        self.current_tutorial_step += 1
        if self.current_tutorial_step < 3:
            self.update_tutorial_step()
        else:
            # End tutorial and go to main page
            self.tutorial_page.fade_out(self.main_page)

    def show_welcome_back(self):
        """Show personalized welcome back message before main content"""
        name = self.data.username or "User"
        self.welcome_back_page.widget.setText(f"Welcome back, {name}!")
        self.welcome_back_page.widget.setStyleSheet("color: #434190; font-weight: bold;")
        self.ask_page.fade_out(self.welcome_back_page)
        QTimer.singleShot(1500, lambda: self.welcome_back_page.fade_out(self.main_page))

    def create_main_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
    
        self.sidebar = QFrame()
        self.sidebar.setMaximumWidth(0)
        self.sidebar.setStyleSheet("background-color: #2d3436; color: white;")
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(10, 20, 10, 10)
    
        for text in ["Home", "Profile", "Settings", "Statistics", "Saved Flashcards"]:
            btn = QPushButton(text)
            btn.setStyleSheet(SIDEBAR_BUTTON_STYLE)
    
            if text == "Saved Flashcards":
                btn.clicked.connect(self.show_saved_flashcards)
            else:
                btn.clicked.connect(lambda _, t=text: self.show_page(t))
                
            side_layout.addWidget(btn)
    
        side_layout.addStretch()
    
        pixmap = QPixmap("Remora-Main.png")
        pixmap = pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        self.existing_flashcard = QPushButton("Existing Flashcards")
        self.existing_flashcard.setFont(FONT_LARGE_BOLD)
        self.existing_flashcard.setStyleSheet(CREATE_FLASH)
        self.existing_flashcard.clicked.connect(self.toggle_existing_flashcard)
    
        self.create_flashcard = QPushButton("Create Flashcard")
        self.create_flashcard.setFont(FONT_LARGE_BOLD)
        self.create_flashcard.setStyleSheet(CREATE_FLASH)
        self.create_flashcard.clicked.connect(self.toggle_create_flashcard)
    
        self.saved_flashcard_btn = QPushButton("Saved Flashcards")
        self.saved_flashcard_btn.setFont(FONT_LARGE_BOLD)
        self.saved_flashcard_btn.setStyleSheet(CREATE_FLASH)
        self.saved_flashcard_btn.clicked.connect(self.show_saved_flashcards)
    
        self.hamburger = QPushButton("☰")
        self.hamburger.setStyleSheet(HAMBURGER_STYLE)
        self.hamburger.clicked.connect(self.toggle_sidebar)
    
        top = QHBoxLayout()
        top.addWidget(self.hamburger)
        top.addStretch()
    
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addLayout(top)
        content_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
    
        '''
        self.main_content = QLabel("Welcome to Remora")
        self.main_content.setFont(FONT_LABEL)
        self.main_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.main_content, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacing(8)
        '''
    
        # Buttons area
        btns_row = QVBoxLayout()
        btns_row.setSpacing(30)
        btns_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btns_row.addWidget(self.existing_flashcard)
        btns_row.addSpacing(40)
        btns_row.addWidget(self.create_flashcard)
    
        content_layout.addLayout(btns_row)
        content_layout.addStretch()
    
        layout.addWidget(self.sidebar)
        layout.addLayout(content_layout)
    
        return page
    
    def toggle_create_flashcard(self):
        print(" ")
        

    def show_greet(self):
        name = self.name_input.text().strip()
        
        if not name:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Missing Name")
            msg.setFont(FONT_SUBTITLE)
            msg.setWindowIcon(QIcon("Icon.png"))
            msg.setText("Enter your name before continuing.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setStyleSheet(MESSAGE_WARNING)
            msg.exec()
            return
    
        self.data.username = name
        self.greet_page.widget.setText(f"Hi, {name}!")
        self.greet_page.widget.setStyleSheet("color: #434190")
        self.name_page.fade_out(self.greet_page)
        QTimer.singleShot(1000, lambda: self.show_welcome())

    def create_welcome_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = QPixmap("Icon.png")
        pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("WELCOME!")
        title.setFont(FONT_LARGE_BOLD)
        title.setStyleSheet("color: #FC483D; font-weight: 900; letter-spacing: 2px;")
        
        subtitle = QLabel("Remora is a flashcard for students")
        subtitle.setFont(FONT_LABEL)
        subtitle.setStyleSheet("color: #A0522D; font-weight: bold;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        return widget
    
    def show_welcome(self):
        self.greet_page.fade_out(self.welcome_page)
        QTimer.singleShot(1500, lambda: self.welcome_page.fade_out(self.ask_page))

    def toggle_sidebar(self):
        current_width = self.sidebar.maximumWidth()
        new_width = 180 if current_width == 0 else 0
        anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        anim.setDuration(400)
        anim.setStartValue(current_width)
        anim.setEndValue(new_width)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
        self.sidebar.anim = anim

    def show_page(self, text):
        self.main_content.setText(f"You selected: {text}")
        
        
        #-------BAGONG LAGAY TO------
    def create_existing_flashcard(self):
        """Create the page shown when 'Existing Flashcard' is clicked."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Choose Topics")
        title.setFont(FONT_LARGE_BOLD)
        title.setStyleSheet("color: #434190; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
     
    

        back_btn = QPushButton("⬅ Back to Main")
        back_btn.setFont(FONT_BUTTON)
        back_btn.clicked.connect(lambda: self.existing_flashcard_page.fade_out(self.main_page))
     
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
     
        return widget

    def setup_existing_flashcard_page(self):
         """Setup and add the existing flashcard page to stacked widget."""
         self.existing_flashcard_page = FadeWidget(self.create_existing_flashcard(), self)
         self.stacked.addWidget(self.existing_flashcard_page)
         self.apply_theme()
     
    def toggle_existing_flashcard(self):
        """Show the topics page when 'Existing Flashcards' is clicked."""
        if not hasattr(self, "topics_page"):
            self.setup_topics_page()
        self.main_page.fade_out(self.topics_page)

                
        # ========== INDIVIDUAL TOPIC PAGES ==========
    def create_topic_page(self, topic_name, bg_color, text_color):
        """Create a topic page with flipping flashcards."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        title = QLabel(f"{topic_name} Flashcards")
        title.setFont(QFont("Arial Rounded MT Bold", 26))
        title.setStyleSheet(f"color: {text_color};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # QUESTIONS EXISTING
        qa_sets = {
            "English": [
                ("What is haha?", "haha is a tawa"),
                ("what is huhu?", "huhu is a iyak")
            ],
            "Math": [
                ("1+1", "2"),
                ("2+2", "4")
            ],
            "Science": [
                ("Who discovered gravity?", "Isaac Newton"),
            ],
            "History": [
                ("Who killed Magellan?", "Lapu-Lapu"),
                ("Where is Rizal’s head?", "On the one-peso coin")
            ],
        }

        flashcards_layout = QHBoxLayout()
        flashcards_layout.setSpacing(30)

        for q, a in qa_sets.get(topic_name, []):
            card = FlipCard(q, a, bg_color="#FFFFFF", text_color=text_color)
            flashcards_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("⬅ Back to Topics")
        back_btn.setFont(QFont("Arial", 14))
        back_btn.setFixedWidth(200)
        back_btn.clicked.connect(lambda: self.topic_pages[topic_name].fade_out(self.topics_page))

        layout.addWidget(title)
        layout.addLayout(flashcards_layout)
        layout.addSpacing(40)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        widget.setStyleSheet(f"background-color: {bg_color};")
        return widget

    #-------BAGONG LAGAY TO------
    def create_topics_page(self):
        """Create a stylized topic selection page matching the uploaded design."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header Title
        title = QLabel("TOPICS")
        title.setFont(QFont("Arial Rounded MT Bold", 36, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            background-color: #F08080;
            color: white;
            padding: 20px;
            border-radius: 15px;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)
        layout.addSpacing(20)

        # === Custom function to create each topic row ===
        def make_topic(icon_path, text, bg_color, text_color):
            container = QFrame()
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border-radius: 35px;
                }}
            """)
            container.setFixedHeight(80)

            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(icon_path).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setFixedSize(60, 60)
            icon_label.setStyleSheet("background-color: white; border-radius: 30px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text_label = QLabel(text)
            text_label.setFont(QFont("Arial Rounded MT Bold", 20))
            text_label.setStyleSheet(f"color: {text_color};")
            text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            row = QHBoxLayout()
            row.setContentsMargins(20, 0, 20, 0)
            row.setSpacing(20)
            row.addWidget(icon_label)
            row.addWidget(text_label)
            row.addStretch()

            container.setLayout(row)
            container.mousePressEvent = lambda event: self.show_topic_page(text)

            return container

        # Topic Buttons (icon path, label, background color, text color)
        topics = [
            ("book.png", "English", "#ADD8FF", "#3A4CC0"),
            ("math.png", "Math", "#A5E6A0", "#2E4B2E"),
            ("science.png", "Science", "#FFE8A0", "#D98C00"),
            ("history.png", "History", "#FFB0A0", "#7B2D2D"),
    ]

        # Add topic buttons
        for icon, text, bg_color, text_color in topics:
            layout.addWidget(make_topic(icon, text, bg_color, text_color))

    # Back Button
        back_btn = QPushButton("⬅ Back to Main")
        back_btn.setFont(QFont("Arial", 14))
        back_btn.setFixedWidth(200)
        back_btn.clicked.connect(lambda: self.topics_page.fade_out(self.main_page))
        layout.addSpacing(30)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Background of entire page
        widget.setStyleSheet("background-color: #FFF6E9;")

        return widget

    #-------BAGONG LAGAY TO------
    def setup_topics_page(self):
        """Initialize the topics page."""
        self.topics_page = FadeWidget(self.create_topics_page(), self)
        self.stacked.addWidget(self.topics_page)
        self.apply_theme()

    def toggle_existing_flashcard(self):
        """Show the topics page when 'Existing Flashcards' is clicked."""
        if not hasattr(self, "topics_page"):
            self.setup_topics_page()
        self.main_page.fade_out(self.topics_page)

    def show_topic_page(self, topic_name):
        """Display the selected topic’s flashcard page."""
        if not hasattr(self, "topic_pages"):
            self.topic_pages = {}

        if topic_name not in self.topic_pages:
            bg_colors = {
                "English": "#D8E6FF",
                "Math": "#C9F7C5",
                "Science": "#FFF6BF",
                "History": "#FFD5CC",
            }
            text_colors = {
                "English": "#1A237E",
                "Math": "#1B5E20",
                "Science": "#BF360C",
                "History": "#4E342E",
            }
            page = FadeWidget(
                self.create_topic_page(topic_name, bg_colors[topic_name], text_colors[topic_name]),
                self
            )
            self.topic_pages[topic_name] = page
            self.stacked.addWidget(page)

        self.topics_page.fade_out(self.topic_pages[topic_name])
    
      # ========== CREATE FLASHCARD PAGE ==========
    def create_create_flashcard_page(self):
        """Page for creating a new flashcard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        self.apply_theme()

        title = QLabel("Create Flashcard")
        title.setFont(QFont("Arial Rounded MT Bold", 28))
        title.setStyleSheet("color: #434190;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.q_input = QLineEdit()
        self.q_input.setPlaceholderText("Enter question here...")
        self.q_input.setFont(QFont("Arial", 14))
        self.q_input.setFixedWidth(400)
        self.q_input.setStyleSheet("padding: 8px; border-radius: 10px; border: 2px solid #888;")

        self.a_input = QLineEdit()
        self.a_input.setPlaceholderText("Enter answer here...")
        self.a_input.setFont(QFont("Arial", 14))
        self.a_input.setFixedWidth(400)
        self.a_input.setStyleSheet("padding: 8px; border-radius: 10px; border: 2px solid #888;")

        save_btn = QPushButton("💾 Save Flashcard")
        save_btn.setFont(QFont("Arial Rounded MT Bold", 14))
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 20px; border-radius: 10px;")
        save_btn.clicked.connect(self.save_flashcard)

        back_btn = QPushButton("⬅ Back to Main")
        back_btn.setFont(QFont("Arial Rounded MT Bold", 14))
        back_btn.setStyleSheet("background-color: #888; color: white; padding: 8px 20px; border-radius: 10px;")
        back_btn.clicked.connect(lambda: self.create_flashcard_page.fade_out(self.main_page))

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addWidget(self.q_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.a_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        widget.setStyleSheet("background-color: #FFF6E9;")
        return widget
    
    def setup_create_flashcard_page(self):
        """Initialize and add the Create Flashcard page to stacked widget."""
        self.create_flashcard_page = FadeWidget(self.create_create_flashcard_page(), self)
        self.stacked.addWidget(self.create_flashcard_page)

    def toggle_create_flashcard(self):
        """Show the Create Flashcard page when button is clicked."""
        if not hasattr(self, "create_flashcard_page"):
            self.setup_create_flashcard_page()
        self.main_page.fade_out(self.create_flashcard_page)

    def save_flashcard(self):
        """Save the flashcard temporarily."""
        question = self.q_input.text().strip()
        answer = self.a_input.text().strip()

        if not question or not answer:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Incomplete Flashcard")
            msg.setText("Please fill out both the question and the answer before saving.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setStyleSheet(MESSAGE_WARNING)
            msg.exec()
            return

        # Save to AppData (you can modify this later to save per topic)
        if not hasattr(self.data, "custom_flashcards"):
            self.data.custom_flashcards = []

        self.data.custom_flashcards.append((question, answer))

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Saved!")
        msg.setText("Flashcard saved successfully ✅")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(MESSAGE_WARNING)
        msg.setWindowIcon(QIcon("Icon.png"))
        msg.exec()

        # Clear inputs for next entry
        self.q_input.clear()
        self.a_input.clear()

    # ========== SAVED FLASHCARDS REVIEW PAGE ==========
    def create_saved_flashcards_page(self):
        """Display saved flashcards created by the user."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
    
        title = QLabel("Your Saved Flashcards")
        title.setFont(QFont("Arial Rounded MT Bold", 28))
        title.setStyleSheet("color: #434190;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        # ✅ Use a QWidget to host the horizontal layout (prevents vertical push)
        self.saved_flashcards_container_widget = QWidget()
        self.saved_flashcards_container_widget.setSizePolicy(
            self.saved_flashcards_container_widget.sizePolicy().horizontalPolicy(),
            self.saved_flashcards_container_widget.sizePolicy().verticalPolicy()
        )
        self.saved_flashcards_container = QHBoxLayout(self.saved_flashcards_container_widget)
        self.saved_flashcards_container.setSpacing(30)
        self.saved_flashcards_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        # Back button
        back_btn = QPushButton("⬅ Back to Main")
        back_btn.setFont(QFont("Arial Rounded MT Bold", 14))
        back_btn.setStyleSheet("background-color: #888; color: white; padding: 8px 20px; border-radius: 10px;")
        back_btn.clicked.connect(lambda: self.saved_flashcards_page.fade_out(self.main_page))
    
        layout.addWidget(title)
        # Add the container widget (not the layout) to the vertical layout
        layout.addWidget(self.saved_flashcards_container_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    
        widget.setStyleSheet("background-color: #FFF6E9;")
        return widget
    


    def setup_saved_flashcards_page(self):
        """Initialize the saved flashcards review page."""
        self.saved_flashcards_page = FadeWidget(self.create_saved_flashcards_page(), self)
        self.stacked.addWidget(self.saved_flashcards_page)
        self.apply_theme()


    def show_saved_flashcards(self):
        """Display user-saved flashcards as FlipCards."""
        if not hasattr(self, "saved_flashcards_page"):
            self.setup_saved_flashcards_page()
    
        # Clear previous child widgets from the container widget (safe)
        if hasattr(self, "saved_flashcards_container"):
            layout = self.saved_flashcards_container
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                w = item.widget()
                if w:
                    w.setParent(None)
                else:
                    # if it's a spacer or layout, take it out
                    layout.removeItem(item)
    
        # Populate cards or show a friendly message
        if not hasattr(self.data, "custom_flashcards") or not self.data.custom_flashcards:
            no_card_label = QLabel("No saved flashcards yet! Create some first. 📚")
            no_card_label.setFont(QFont("Arial", 14))
            no_card_label.setStyleSheet("color: #777;")
            no_card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.saved_flashcards_container.addWidget(no_card_label)
        else:
            for q, a in self.data.custom_flashcards:
                card = FlipCard(q, a, bg_color="#FFFFFF", text_color="#333")
                self.saved_flashcards_container.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
    
        # Use your fade transition to show the page
        self.main_page.fade_out(self.saved_flashcards_page)


    def show_saved_flashcards(self):
        """Display user-saved flashcards as FlipCards."""
        # Create the page if it doesn’t exist yet
        if not hasattr(self, "saved_flashcards_page"):
            self.setup_saved_flashcards_page()

        # Clear previous cards (to refresh)
        for i in reversed(range(self.saved_flashcards_container.count())):
            widget_item = self.saved_flashcards_container.itemAt(i).widget()
            if widget_item:
                widget_item.setParent(None)

        # Check if there are saved flashcards
        if not hasattr(self.data, "custom_flashcards") or not self.data.custom_flashcards:
            no_card_label = QLabel("No saved flashcards yet! Create some first. 📚")
            no_card_label.setFont(QFont("Arial", 14))
            no_card_label.setStyleSheet("color: #777;")
            no_card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.saved_flashcards_container.addWidget(no_card_label)
        else:
            # Create FlipCards for each saved flashcard
            for q, a in self.data.custom_flashcards:
                card = FlipCard(q, a, bg_color="#FFFFFF", text_color="#333")
                self.saved_flashcards_container.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_page.fade_out(self.saved_flashcards_page)