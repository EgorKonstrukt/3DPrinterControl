import os
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.themes_path = os.path.join(os.path.dirname(__file__), "..", "styles")

    def apply_theme(self, theme_name):
        style_path = os.path.join(self.themes_path, f"{theme_name}.qss")

        if os.path.exists(style_path):
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                QApplication.instance().setStyleSheet(stylesheet)
                return True
            except Exception as e:
                print(f"Error loading theme {theme_name}: {e}")
                return False
        else:
            self._create_default_themes()
            return self.apply_theme(theme_name)

    def _create_default_themes(self):
        os.makedirs(self.themes_path, exist_ok=True)

        dark_theme = """
        

QWidget{
background-color:#121212;
color:#ffffff;
font-family:"Segoe UI",Arial,sans-serif;
font-size:8pt;
}
QMainWindow{
background-color:#1e1e1e;
color:#ffffff;
}
QMenuBar{
background-color:rgba(30,30,30,0.7);
color:#ffffff;
border-bottom:1px solid #444444;
}
QMenuBar::item{
background-color:transparent;
padding:2px 4px;
}
QMenuBar::item:selected{
background-color:#e51400;
}
QMenu{
background-color:rgba(30,30,30,0.95);
color:#ffffff;
border:1px solid #444444;
}
QMenu::item{
padding:2px 8px;
}
QMenu::item:selected{
background-color:#e51400;
}
QStatusBar{
background-color:rgba(30,30,30,0.7);
color:#ffffff;
border-top:1px solid #444444;
}
QPushButton{
background-color:#2a2a2a;
color:#ffffff;
border:1px solid #444444;
border-radius:2px;
padding:2px 4px;
font-weight:bold;
min-height:20px;
}
QPushButton:hover{
background-color:#3a3a3a;
border-color:#e51400;
}
QPushButton:pressed{
background-color:#1a1a1a;
border-color:#b51000;
}
QPushButton:disabled{
background-color:#151515;
color:#555555;
border-color:#333333;
}
QPushButton:checked{
background-color:#e51400;
border-color:#c41100;
}
QPushButton[class="success"]{
background-color:#4caf50;
border-color:#3d8b40;
}
QPushButton[class="success"]:hover{
background-color:#5cbf60;
}
QPushButton[class="danger"]{
background-color:#e51400;
border-color:#b51000;
}
QPushButton[class="danger"]:hover{
background-color:#ff3a20;
}
QPushButton[class="warning"]{
background-color:#ff9800;
border-color:#e08800;
}
QPushButton[class="warning"]:hover{
background-color:#ffb74d;
}
QLineEdit,QTextEdit,QPlainTextEdit{
background-color:#252525;
color:#ffffff;
border:1px solid #444444;
border-radius:2px;
padding:2px 4px;
selection-background-color:#e51400;
}
QLineEdit:focus,QTextEdit:focus,QPlainTextEdit:focus{
border-color:#e51400;
}
QLineEdit:disabled,QTextEdit:disabled,QPlainTextEdit:disabled{
background-color:#151515;
color:#555555;
border-color:#333333;
}
QSpinBox,QDoubleSpinBox{
background-color:#252525;
color:#ffffff;
border:1px solid #444444;
border-radius:2px;
padding:2px 4px;
}
QSpinBox:focus,QDoubleSpinBox:focus{
border-color:#e51400;
}
QSpinBox::up-button,QDoubleSpinBox::up-button{
background-color:#2a2a2a;
border:1px solid #444444;
border-radius:2px;
width:14px;
}
QSpinBox::up-button:hover,QDoubleSpinBox::up-button:hover{
background-color:#3a3a3a;
}
QSpinBox::down-button,QDoubleSpinBox::down-button{
background-color:#2a2a2a;
border:1px solid #444444;
border-radius:2px;
width:14px;
}
QSpinBox::down-button:hover,QDoubleSpinBox::down-button:hover{
background-color:#3a3a3a;
}
QComboBox{
background-color:#252525;
color:#ffffff;
border:1px solid #444444;
border-radius:2px;
padding:2px 4px;
}
QComboBox:focus{
border-color:#e51400;
}
QComboBox::drop-down{
background-color:#2a2a2a;
border:none;
border-radius:2px;
width:18px;
}
QComboBox::down-arrow{
image:url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iNiIgdmlld0JveD0iMCAwIDEwIDYiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNSA1TDkgMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}
QComboBox QAbstractItemView{
background-color:#252525;
color:#ffffff;
border:1px solid #444444;
selection-background-color:#e51400;
}
QCheckBox{
color:#ffffff;
spacing:1px;
}
QCheckBox::indicator{
width:14px;
height:14px;
background-color:#252525;
border:1px solid #444444;
border-radius:2px;
}
QCheckBox::indicator:hover{
border-color:#e51400;
}
QCheckBox::indicator:checked{
background-color:#e51400;
border-color:#c41100;
image:url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
}
QRadioButton{
color:#ffffff;
spacing:1px;
}
QRadioButton::indicator{
width:14px;
height:14px;
background-color:#252525;
border:1px solid #444444;
border-radius:7px;
}
QRadioButton::indicator:hover{
border-color:#e51400;
}
QRadioButton::indicator:checked{
background-color:#e51400;
border-color:#c41100;
}
QRadioButton::indicator:checked::after{
content:"";
width:6px;
height:6px;
border-radius:3px;
background-color:#ffffff;
margin:3px;
}
QSlider::groove:horizontal{
background-color:#252525;
height:4px;
border-radius:2px;
}
QSlider::handle:horizontal{
background-color:#e51400;
width:14px;
height:14px;
border-radius:7px;
margin:-5px 0;
}
QSlider::handle:horizontal:hover{
background-color:#ff3a20;
}
QSlider::groove:vertical{
background-color:#252525;
width:4px;
border-radius:2px;
}
QSlider::handle:vertical{
background-color:#e51400;
width:14px;
height:14px;
border-radius:7px;
margin:0 -5px;
}
QSlider::handle:vertical:hover{
background-color:#ff3a20;
}
QProgressBar{
background-color:#252525;
border:1px solid #444444;
border-radius:2px;
text-align:center;
color:#ffffff;
}
QProgressBar::chunk{
background-color:#e51400;
border-radius:1px;
}
QGroupBox{
color:#ffffff;
border:1px solid #444444;
border-radius:2px;
margin-top:2px;
padding-top:2px;
font-weight:bold;
}
QGroupBox::title{
subcontrol-origin:margin;
left:6px;
padding:0 2px 0 2px;
background-color:#1e1e1e;
}
QTabWidget::pane{
background-color:#1e1e1e;
border:1px solid #444444;
border-radius:2px;
}
QTabBar::tab{
background-color:#252525;
color:#ffffff;
border:1px solid #444444;
border-bottom:none;
border-radius:2px 2px 0 0;
padding:1px 2px;
margin-right:1px;
}
QTabBar::tab:selected{
background-color:#e51400;
border-color:#c41100;
}
QTabBar::tab:hover:!selected{
background-color:#3a3a3a;
}
QDockWidget{
background-color:#1e1e1e;
color:#ffffff;
border:1px solid #444444;
}
QDockWidget::title{
background-color:#252525;
color:#ffffff;
padding:1px 2px;
border-bottom:1px solid #444444;
font-weight:bold;
}
QDockWidget::close-button,QDockWidget::float-button{
background-color:#e51400;
color:#ffffff;
border:1px solid #c41100;
border-radius:2px;
width:14px;
height:14px;
}
QDockWidget::close-button:hover,QDockWidget::float-button:hover{
background-color:#ff3a20;
}
QSplitter::handle{
background-color:#444444;
}
QSplitter::handle:horizontal{
width:1px;
}
QSplitter::handle:vertical{
height:1px;
}
QSplitter::handle:hover{
background-color:#e51400;
}
QScrollBar:vertical{
background-color:#252525;
width:10px;
border-radius:5px;
}
QScrollBar::handle:vertical{
background-color:#444444;
border-radius:5px;
min-height:15px;
}
QScrollBar::handle:vertical:hover{
background-color:#e51400;
}
QScrollBar:horizontal{
background-color:#252525;
height:10px;
border-radius:5px;
}
QScrollBar::handle:horizontal{
background-color:#444444;
border-radius:5px;
min-width:15px;
}
QScrollBar::handle:horizontal:hover{
background-color:#e51400;
}
QTableWidget,QTableView{
background-color:#1e1e1e;
color:#ffffff;
border:1px solid #444444;
gridline-color:#333333;
selection-background-color:#e51400;
}
QTableWidget::item,QTableView::item{
padding:2px 4px;
border-bottom:1px solid #333333;
}
QHeaderView::section{
background-color:#252525;
color:#ffffff;
border:1px solid #444444;
padding:2px 4px;
font-weight:bold;
}
QListWidget,QListView{
background-color:#1e1e1e;
color:#ffffff;
border:1px solid #444444;
selection-background-color:#e51400;
}
QListWidget::item,QListView::item{
padding:2px 4px;
border-bottom:1px solid #333333;
}
QListWidget::item:hover,QListView::item:hover{
background-color:#252525;
}
QTreeWidget,QTreeView{
background-color:#1e1e1e;
color:#ffffff;
border:1px solid #444444;
selection-background-color:#e51400;
}
QTreeWidget::item,QTreeView::item{
padding:1px 2px;
border-bottom:1px solid #333333;
}
QTreeWidget::item:hover,QTreeView::item:hover{
background-color:#252525;
}
QTreeWidget::branch:closed:has-children{
image:url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMiAyTDYgNEwyIDYiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}
QTreeWidget::branch:open:has-children{
image:url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMiAyTDQgNkw2IDIiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}
QDialog{
background-color:#1e1e1e;
color:#ffffff;
}
QMessageBox{
background-color:#1e1e1e;
color:#ffffff;
}
QMessageBox QPushButton{
min-width:70px;
}
QToolTip{
background-color:rgba(30,30,30,0.95);
color:#ffffff;
border:1px solid #444444;
border-radius:2px;
padding:3px 6px;
}
QTextEdit[class="console"]{
background-color:#151515;
color:#ffffff;
font-family:"Consolas","Courier New",monospace;
font-size:9pt;
border:1px solid #444444;
}
QOpenGLWidget{
border:1px solid #444444;
border-radius:2px;
}
QPushButton{
transition:all 0.2s ease;
}
QLineEdit,QTextEdit,QComboBox,QSpinBox,QDoubleSpinBox{
transition:border-color 0.2s ease;
}
QFrame[frameShape="4"]{
color:#444444;
}
QFrame[frameShape="5"]{
color:#444444;
}
QWidget[class="control-panel"]{
background-color:#252525;
border:1px solid #444444;
border-radius:2px;
}
QLabel[class="title"]{
font-size:12pt;
font-weight:bold;
color:#e51400;
}
QLabel[class="subtitle"]{
font-size:10pt;
font-weight:bold;
color:#cccccc;
}
QLabel[class="status-connected"]{
color:#4caf50;
font-weight:bold;
}
QLabel[class="status-disconnected"]{
color:#e51400;
font-weight:bold;
}
QLabel[class="status-warning"]{
color:#ff9800;
font-weight:bold;
}


        """

        light_theme = """
        
        QMainWindow {
            background-color: #f0f0f0;
            color: #000000;
        }

        QDockWidget {
            background-color: #ffffff;
            color: #000000;
        }

        QDockWidget::title {
            background-color: #e0e0e0;
            padding: 3px;
            border: 1px solid #c0c0c0;
        }

        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
            border-bottom: 1px solid #c0c0c0;
        }

        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }

        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
        }

        QMenu::item:selected {
            background-color: #e0e0e0;
        }

        QToolBar {
            background-color: #f0f0f0;
            border: 1px solid #c0c0c0;
        }

        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
            border-top: 1px solid #c0c0c0;
        }

        QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 5px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #f0f0f0;
        }

        QPushButton:pressed {
            background-color: #e0e0e0;
        }

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 3px;
            border-radius: 2px;
        }

        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
        }

        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: #ffffff;
        }

        QTabBar::tab {
            background-color: #f0f0f0;
            color: #000000;
            padding: 5px 10px;
            border: 1px solid #c0c0c0;
            border-bottom: none;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
        }

        QGroupBox {
            color: #000000;
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        QCheckBox {
            color: #000000;
        }

        QSlider::groove:horizontal {
            border: 1px solid #c0c0c0;
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #0078d4;
            border: 1px solid #0078d4;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        
        """

        try:
            with open(os.path.join(self.themes_path, "dark.qss"), 'w', encoding='utf-8') as f:
                f.write(dark_theme)

            with open(os.path.join(self.themes_path, "light.qss"), 'w', encoding='utf-8') as f:
                f.write(light_theme)
        except Exception as e:
            print(f"Error creating default themes: {e}")