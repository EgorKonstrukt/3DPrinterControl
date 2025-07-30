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
        

/* Основные цвета */
QWidget {
    background-color: #141414;
    color: #ffffff;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 9pt;
}

/* Главное окно */
QMainWindow {
    background-color: #1f1f1f;
    color: #ffffff;
}

/* Меню */
QMenuBar {
    background-color: #3c3c3c;
    color: #ffffff;
    border-bottom: 1px solid #555555;
}

QMenuBar::item {
    background-color: transparent;
    padding: 3px 5px;
}

QMenuBar::item:selected {
    background-color: #4a90e2;
}

QMenu {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
}

QMenu::item {
    padding: 3px 10px;
}

QMenu::item:selected {
    background-color: #4a90e2;
}

/* Статусная строка */
QStatusBar {
    background-color: #3c3c3c;
    color: #ffffff;
    border-top: 1px solid #555555;
}

/* Кнопки */
QPushButton {
    background-color: #4a4a4a;
    color: #ffffff;
    border: 1px solid #777777;
    border-radius: 2px;
    padding: 3px 3px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #5a5a5a;
    border-color: #777777;
}

QPushButton:pressed {
    background-color: #3a3a3a;
    border-color: #555555;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666666;
    border-color: #444444;
}

QPushButton:checked {
    background-color: #4a90e2;
    border-color: #3a7bc8;
}

/* Специальные кнопки */
QPushButton[class="success"] {
    background-color: #4caf50;
    border-color: #45a049;
}

QPushButton[class="success"]:hover {
    background-color: #5cbf60;
}

QPushButton[class="danger"] {
    background-color: #f44336;
    border-color: #da190b;
}

QPushButton[class="danger"]:hover {
    background-color: #f66356;
}

QPushButton[class="warning"] {
    background-color: #ff9800;
    border-color: #e68900;
}

QPushButton[class="warning"]:hover {
    background-color: #ffb74d;
}

/* Поля ввода */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 3px 5px;
    selection-background-color: #4a90e2;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #4a90e2;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #2a2a2a;
    color: #666666;
    border-color: #444444;
}

/* Спинбоксы */
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 3px 5px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #4a90e2;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #4a4a4a;
    border: 1px solid #666666;
    border-radius: 2px;
    width: 16px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #5a5a5a;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #4a4a4a;
    border: 1px solid #666666;
    border-radius: 2px;
    width: 16px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #5a5a5a;
}

/* Комбобоксы */
QComboBox {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 3px 5px;
}

QComboBox:focus {
    border-color: #4a90e2;
}

QComboBox::drop-down {
    background-color: #4a4a4a;
    border: none;
    border-radius: 2px;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iNiIgdmlld0JveD0iMCAwIDEwIDYiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNSA1TDkgMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    selection-background-color: #4a90e2;
}

/* Чекбоксы */
QCheckBox {
    color: #ffffff;
    spacing: 2px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background-color: #3c3c3c;
    border: 1px solid #666666;
    border-radius: 2px;
}

QCheckBox::indicator:hover {
    border-color: #4a90e2;
}

QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border-color: #3a7bc8;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
}

/* Радиокнопки */
QRadioButton {
    color: #ffffff;
    spacing: 2px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    background-color: #3c3c3c;
    border: 1px solid #666666;
    border-radius: 8px;
}

QRadioButton::indicator:hover {
    border-color: #4a90e2;
}

QRadioButton::indicator:checked {
    background-color: #4a90e2;
    border-color: #3a7bc8;
}

QRadioButton::indicator:checked::after {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 3px;
    background-color: #ffffff;
    margin: 3px;
}

/* Слайдеры */
QSlider::groove:horizontal {
    background-color: #3c3c3c;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #4a90e2;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}

QSlider::handle:horizontal:hover {
    background-color: #5ba0f2;
}

QSlider::groove:vertical {
    background-color: #3c3c3c;
    width: 6px;
    border-radius: 3px;
}

QSlider::handle:vertical {
    background-color: #4a90e2;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: 0 -6px;
}

QSlider::handle:vertical:hover {
    background-color: #5ba0f2;
}

/* Прогресс-бары */
QProgressBar {
    background-color: #3c3c3c;
    border: 1px solid #666666;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #4a90e2;
    border-radius: 3px;
}

/* Группы */
QGroupBox {
    color: #ffffff;
    border: 1px solid #666666;
    border-radius: 4px;
    margin-top: 3px;
    padding-top: 3px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 3px 0 3px;
    background-color: #2b2b2b;
}

/* Вкладки */
QTabWidget::pane {
    background-color: #2b2b2b;
    border: 1px solid #666666;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    padding: 2px 3px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #4a90e2;
    border-color: #3a7bc8;
}

QTabBar::tab:hover:!selected {
    background-color: #4a4a4a;
}

/* Докинг виджеты */
QDockWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #666666;
}

QDockWidget::title {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 2px 3px;
    border-bottom: 1px solid #666666;
    font-weight: bold;
}

QDockWidget::close-button, QDockWidget::float-button {
    background-color: #ff1414;
    color: #b52b2b;
    border: 1px solid #666666;
    border-radius: 2px;
    width: 16px;
    height: 16px;
}

QDockWidget::close-button:hover, QDockWidget::float-button:hover {
    background-color: #5a5a5a;
}

/* Сплиттеры */
QSplitter::handle {
    background-color: #b52b2b;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #4a90e2;
}

/* Скроллбары */
QScrollBar:vertical {
    background-color: #3c3c3c;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #666666;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #777777;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #3c3c3c;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #666666;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #777777;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Таблицы */
QTableWidget, QTableView {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #666666;
    gridline-color: #666666;
    selection-background-color: #4a90e2;
}

QTableWidget::item, QTableView::item {
    padding: 4px 8px;
    border-bottom: 1px solid #666666;
}

QHeaderView::section {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    padding: 4px 8px;
    font-weight: bold;
}

/* Списки */
QListWidget, QListView {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #666666;
    selection-background-color: #4a90e2;
}

QListWidget::item, QListView::item {
    padding: 4px 8px;
    border-bottom: 1px solid #666666;
}

QListWidget::item:hover, QListView::item:hover {
    background-color: #3c3c3c;
}

/* Деревья */
QTreeWidget, QTreeView {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #666666;
    selection-background-color: #4a90e2;
}

QTreeWidget::item, QTreeView::item {
    padding: 2px 4px;
    border-bottom: 1px solid #666666;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #3c3c3c;
}

QTreeWidget::branch:closed:has-children {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMiAyTDYgNEwyIDYiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

QTreeWidget::branch:open:has-children {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMiAyTDQgNkw2IDIiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

/* Диалоги */
QDialog {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMessageBox {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* Тултипы */
QToolTip {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 4px 8px;
}

/* Специальные стили для консоли */
QTextEdit[class="console"] {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10pt;
    border: 1px solid #555555;
}

/* Специальные стили для 3D визуализации */
QOpenGLWidget {
    border: 1px solid #666666;
    border-radius: 4px;
}

/* Анимации */
QPushButton {
    transition: all 0.2s ease;
}

QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    transition: border-color 0.2s ease;
}

/* Дополнительные стили для улучшенного внешнего вида */
QFrame[frameShape="4"] { /* HLine */
    color: #666666;
}

QFrame[frameShape="5"] { /* VLine */
    color: #666666;
}

/* Стили для кастомных виджетов */
QWidget[class="control-panel"] {
    background-color: #3c3c3c;
    border: 1px solid #666666;
    border-radius: 4px;
}

QLabel[class="title"] {
    font-size: 14pt;
    font-weight: bold;
    color: #4a90e2;
}

QLabel[class="subtitle"] {
    font-size: 11pt;
    font-weight: bold;
    color: #cccccc;
}

QLabel[class="status-connected"] {
    color: #4caf50;
    font-weight: bold;
}

QLabel[class="status-disconnected"] {
    color: #f44336;
    font-weight: bold;
}

QLabel[class="status-warning"] {
    color: #ff9800;
    font-weight: bold;
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