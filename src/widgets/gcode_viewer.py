import os
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QPlainTextEdit, QProgressBar, QFileDialog,
                             QGroupBox, QGridLayout, QSpinBox, QCheckBox,
                             QTabWidget, QListWidget, QListWidgetItem,
                             QSplitter, QFrame, QSlider, QComboBox, QLayout,
                             QAbstractScrollArea, QScrollBar, QTextEdit, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex, QRect, QSize, QRegularExpression
from PyQt5.QtGui import QFont, QTextCursor, QColor, QTextCharFormat, QSyntaxHighlighter, QPainter, \
    QTextFormat


class LineNumberArea(QWidget):
    def init(self, editor):
        super().init(editor)
        self.code_editor = editor


class GCodeHighlighter(QSyntaxHighlighter):
    def init(self, parent=None):
        super().init(parent)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569CD6"))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        self.movement_format = QTextCharFormat()
        self.movement_format.setForeground(QColor("#C586C0"))

        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor("#B5CEA8"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#608B4E"))
        self.comment_format.setFontItalic(True)

        self.rules = [
            (QRegularExpression(r"\bG[0-9]+\b"), self.keyword_format),
            (QRegularExpression(r"\bM[0-9]+\b"), self.keyword_format),
            (QRegularExpression(r"\bT[0-9]+\b"), self.keyword_format),
            (QRegularExpression(r"\bF[0-9.]+\b"), self.movement_format),
            (QRegularExpression(r"\bX[0-9.-]+\b"), self.movement_format),
            (QRegularExpression(r"\bY[0-9.-]+\b"), self.movement_format),
            (QRegularExpression(r"\bZ[0-9.-]+\b"), self.movement_format),
            (QRegularExpression(r"\bE[0-9.-]+\b"), self.movement_format),
            (QRegularExpression(r"[0-9]+(\.[0-9]*)?"), self.value_format),
            (QRegularExpression(r";.*$"), self.comment_format),
        ]


    def highlightBlock(self, text):
        for pattern, format in self.rules:
            expression = QRegularExpression(pattern)
            match = expression.match(text)
            while match.hasMatch():
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, format)
                match = expression.match(text, start + length)




    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)


    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class GCodeViewer(QWidget):
    file_loaded = pyqtSignal(str)
    print_started = pyqtSignal()
    layer_selected = pyqtSignal(int)


    def __init__(self, gcode_handler):
        super().__init__()
        self.gcode_handler = gcode_handler
        self.gcode_commands = []
        self.current_file = ""
        self.analysis_data = {}
        self.layers_data = []
        self.highlighter = None

        self.init_ui()
        self.connect_signals()


    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        file_group = QGroupBox("Управление файлом G-кода")
        file_layout = QHBoxLayout()
        file_group.setLayout(file_layout)

        self.load_file_btn = QPushButton("Загрузить G-код")
        self.load_file_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")

        self.reload_file_btn = QPushButton("Перезагрузить")
        self.reload_file_btn.setEnabled(False)

        self.file_label = QLabel("Файл не загружен")
        self.file_label.setStyleSheet("QLabel { color: #888888; font-style: italic; }")

        file_layout.addWidget(self.load_file_btn)
        file_layout.addWidget(self.reload_file_btn)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()

        layout.addWidget(file_group, 0)

        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter, 1)

        left_panel = QTabWidget()
        main_splitter.addWidget(left_panel)

        preview_tab = self.create_preview_tab()
        left_panel.addTab(preview_tab, "Код")

        analysis_tab = self.create_analysis_tab()
        left_panel.addTab(analysis_tab, "Анализ")

        layers_tab = self.create_layers_tab()
        left_panel.addTab(layers_tab, "Слои")

        right_panel = self.create_control_panel()
        main_splitter.addWidget(right_panel)

        main_splitter.setSizes([600, 300])


    def create_preview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        controls_layout = QHBoxLayout()

        self.line_numbers_checkbox = QCheckBox("Номера строк")
        self.line_numbers_checkbox.setChecked(True)

        self.highlight_moves_checkbox = QCheckBox("Подсветка движений")
        self.highlight_moves_checkbox.setChecked(True)

        self.filter_comments_checkbox = QCheckBox("Скрыть комментарии")

        self.syntax_highlight_checkbox = QCheckBox("Подсветка синтаксиса")
        self.syntax_highlight_checkbox.setChecked(True)

        controls_layout.addWidget(self.line_numbers_checkbox)
        controls_layout.addWidget(self.highlight_moves_checkbox)
        controls_layout.addWidget(self.filter_comments_checkbox)
        controls_layout.addWidget(self.syntax_highlight_checkbox)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self.gcode_text = QPlainTextEdit()
        self.gcode_text.setReadOnly(True)
        self.gcode_text.setFont(QFont("Consolas", 10))
        self.gcode_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #3399ff;
                line-height: 1.2;
            }
        """)

        self.line_number_area = LineNumberArea(self.gcode_text)

        self.gcode_text.blockCountChanged.connect(self.update_line_number_area_width)
        self.gcode_text.updateRequest.connect(self.update_line_number_area)
        self.gcode_text.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        container = QWidget()
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container.setLayout(container_layout)

        container_layout.addWidget(self.line_number_area, 0)
        container_layout.addWidget(self.gcode_text, 1)

        layout.addWidget(container)

        navigation_layout = QHBoxLayout()

        self.goto_line_input = QSpinBox()
        self.goto_line_input.setRange(1, 1)
        self.goto_line_input.setPrefix("Строка: ")

        self.goto_line_btn = QPushButton("Перейти")
        self.goto_line_btn.clicked.connect(self.goto_line)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Поиск...")

        self.find_btn = QPushButton("Найти")
        self.find_btn.clicked.connect(self.find_text)

        navigation_layout.addWidget(self.goto_line_input)
        navigation_layout.addWidget(self.goto_line_btn)
        navigation_layout.addStretch()
        navigation_layout.addWidget(self.find_input)
        navigation_layout.addWidget(self.find_btn)

        layout.addLayout(navigation_layout)

        return widget


    def line_number_area_width(self):
        digits = 1
        count = max(1, self.gcode_text.blockCount())
        while count >= 10:
            count //= 10
            digits += 1
        space = 3 + self.gcode_text.fontMetrics().horizontalAdvance('9') * digits
        return space


    def update_line_number_area_width(self, newBlockCount):
        self.gcode_text.setViewportMargins(self.line_number_area_width(), 0, 0, 0)


    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.gcode_text.viewport().rect()):
            self.update_line_number_area_width(0)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.gcode_text.contentsRect()
        width = self.line_number_area_width()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), width, cr.height()))


    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2b2b2b"))

        block = self.gcode_text.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.gcode_text.blockBoundingGeometry(block).translated(self.gcode_text.contentOffset()).top()
        bottom = top + self.gcode_text.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#888888"))
                painter.drawText(0, int(top), self.line_number_area.width(),
                                 self.gcode_text.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.gcode_text.blockBoundingRect(block).height()
            block_number += 1


    def highlight_current_line(self):
        extra_selections = []
        if not self.gcode_text.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#303030")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.gcode_text.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.gcode_text.setExtraSelections(extra_selections)


    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        info_group = QGroupBox("Основная информация")
        info_layout = QGridLayout()
        info_group.setLayout(info_layout)

        self.total_lines_label = QLabel("0")
        self.layer_count_label = QLabel("0")
        self.print_time_label = QLabel("Неизвестно")
        self.filament_length_label = QLabel("0.0 м")

        info_layout.addWidget(QLabel("Всего строк:"), 0, 0)
        info_layout.addWidget(self.total_lines_label, 0, 1)
        info_layout.addWidget(QLabel("Количество слоев:"), 1, 0)
        info_layout.addWidget(self.layer_count_label, 1, 1)
        info_layout.addWidget(QLabel("Время печати:"), 2, 0)
        info_layout.addWidget(self.print_time_label, 2, 1)
        info_layout.addWidget(QLabel("Длина филамента:"), 3, 0)
        info_layout.addWidget(self.filament_length_label, 3, 1)

        layout.addWidget(info_group)

        temp_group = QGroupBox("Температурные настройки")
        temp_layout = QGridLayout()
        temp_group.setLayout(temp_layout)

        self.max_extruder_temp_label = QLabel("0°C")
        self.max_bed_temp_label = QLabel("0°C")

        temp_layout.addWidget(QLabel("Макс. температура экструдера:"), 0, 0)
        temp_layout.addWidget(self.max_extruder_temp_label, 0, 1)
        temp_layout.addWidget(QLabel("Макс. температура стола:"), 1, 0)
        temp_layout.addWidget(self.max_bed_temp_label, 1, 1)

        layout.addWidget(temp_group)

        bounds_group = QGroupBox("Размеры и границы модели")
        bounds_layout = QGridLayout()
        bounds_group.setLayout(bounds_layout)

        self.bounds_x_label = QLabel("0.0 мм")
        self.bounds_y_label = QLabel("0.0 мм")
        self.bounds_z_label = QLabel("0.0 мм")
        self.center_x_label = QLabel("0.0 мм")
        self.center_y_label = QLabel("0.0 мм")

        bounds_layout.addWidget(QLabel("Размер по X:"), 0, 0)
        bounds_layout.addWidget(self.bounds_x_label, 0, 1)
        bounds_layout.addWidget(QLabel("Размер по Y:"), 1, 0)
        bounds_layout.addWidget(self.bounds_y_label, 1, 1)
        bounds_layout.addWidget(QLabel("Высота (Z):"), 2, 0)
        bounds_layout.addWidget(self.bounds_z_label, 2, 1)
        bounds_layout.addWidget(QLabel("Центр X:"), 3, 0)
        bounds_layout.addWidget(self.center_x_label, 3, 1)
        bounds_layout.addWidget(QLabel("Центр Y:"), 4, 0)
        bounds_layout.addWidget(self.center_y_label, 4, 1)

        layout.addWidget(bounds_group)

        moves_group = QGroupBox("Статистика движений")
        moves_layout = QGridLayout()
        moves_group.setLayout(moves_layout)

        self.print_moves_label = QLabel("0")
        self.travel_moves_label = QLabel("0")
        self.retractions_label = QLabel("0")

        moves_layout.addWidget(QLabel("Движения печати:"), 0, 0)
        moves_layout.addWidget(self.print_moves_label, 0, 1)
        moves_layout.addWidget(QLabel("Перемещения:"), 1, 0)
        moves_layout.addWidget(self.travel_moves_label, 1, 1)
        moves_layout.addWidget(QLabel("Ретракты:"), 2, 0)
        moves_layout.addWidget(self.retractions_label, 2, 1)

        layout.addWidget(moves_group)

        layout.addStretch()
        return widget


    def create_layers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        layers_group = QGroupBox("Слои модели")
        layers_layout = QVBoxLayout()
        layers_group.setLayout(layers_layout)

        self.layers_list = QListWidget()
        self.layers_list.itemClicked.connect(self.on_layer_selected)
        layers_layout.addWidget(self.layers_list)

        layer_info_layout = QHBoxLayout()

        self.layer_info_label = QLabel("Выберите слой для просмотра информации")
        layer_info_layout.addWidget(self.layer_info_label)

        layers_layout.addLayout(layer_info_layout)

        layout.addWidget(layers_group)

        filter_group = QGroupBox("Фильтры отображения")
        filter_layout = QGridLayout()
        filter_group.setLayout(filter_layout)

        self.show_print_moves_cb = QCheckBox("Показать печать")
        self.show_print_moves_cb.setChecked(True)

        self.show_travel_moves_cb = QCheckBox("Показать перемещения")
        self.show_travel_moves_cb.setChecked(True)

        self.show_retractions_cb = QCheckBox("Показать ретракты")
        self.show_retractions_cb.setChecked(True)

        filter_layout.addWidget(self.show_print_moves_cb, 0, 0)
        filter_layout.addWidget(self.show_travel_moves_cb, 0, 1)
        filter_layout.addWidget(self.show_retractions_cb, 1, 0)

        layout.addWidget(filter_group)

        layout.addStretch()
        return widget


    def create_control_panel(self):
        widget = QWidget()
        widget.setMaximumWidth(300)
        widget.setMinimumWidth(250)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        print_controls_group = QGroupBox("Управление печатью")
        print_controls_layout = QGridLayout()
        print_controls_group.setLayout(print_controls_layout)

        self.start_print_btn = QPushButton("Начать печать")
        self.start_print_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.start_print_btn.setEnabled(False)

        self.pause_print_btn = QPushButton("Пауза")
        self.pause_print_btn.setEnabled(False)

        self.resume_print_btn = QPushButton("Продолжить")
        self.resume_print_btn.setEnabled(False)

        self.stop_print_btn = QPushButton("Остановить")
        self.stop_print_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 10px; }")
        self.stop_print_btn.setEnabled(False)

        print_controls_layout.addWidget(self.start_print_btn, 0, 0, 1, 2)
        print_controls_layout.addWidget(self.pause_print_btn, 1, 0)
        print_controls_layout.addWidget(self.resume_print_btn, 1, 1)
        print_controls_layout.addWidget(self.stop_print_btn, 2, 0, 1, 2)

        layout.addWidget(print_controls_group)

        progress_group = QGroupBox("Прогресс печати")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)

        self.print_progress = QProgressBar()
        self.print_progress.setRange(0, 100)
        self.print_progress.setValue(0)
        self.print_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)

        self.progress_label = QLabel("Готов к печати")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("QLabel { font-weight: bold; }")

        self.time_remaining_label = QLabel("Время: --:--")
        self.time_remaining_label.setAlignment(Qt.AlignCenter)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.print_progress)
        progress_layout.addWidget(self.time_remaining_label)

        layout.addWidget(progress_group)

        layer_control_group = QGroupBox("Навигация по слоям")
        layer_control_layout = QVBoxLayout()
        layer_control_group.setLayout(layer_control_layout)

        self.layer_slider = QSlider(Qt.Horizontal)
        self.layer_slider.setRange(0, 0)
        self.layer_slider.setValue(0)
        self.layer_slider.valueChanged.connect(self.on_layer_slider_changed)

        self.current_layer_label = QLabel("Слой: 0 / 0")
        self.current_layer_label.setAlignment(Qt.AlignCenter)
        self.current_layer_label.setStyleSheet("QLabel { font-weight: bold; }")

        layer_nav_layout = QHBoxLayout()

        self.first_layer_btn = QPushButton("⏮")
        self.first_layer_btn.setMaximumWidth(40)
        self.first_layer_btn.setToolTip("Первый слой")

        self.prev_layer_btn = QPushButton("◀")
        self.prev_layer_btn.setMaximumWidth(40)
        self.prev_layer_btn.setToolTip("Предыдущий слой")

        self.next_layer_btn = QPushButton("▶")
        self.next_layer_btn.setMaximumWidth(40)
        self.next_layer_btn.setToolTip("Следующий слой")

        self.last_layer_btn = QPushButton("⏭")
        self.last_layer_btn.setMaximumWidth(40)
        self.last_layer_btn.setToolTip("Последний слой")

        layer_nav_layout.addWidget(self.first_layer_btn)
        layer_nav_layout.addWidget(self.prev_layer_btn)
        layer_nav_layout.addStretch()
        layer_nav_layout.addWidget(self.next_layer_btn)
        layer_nav_layout.addWidget(self.last_layer_btn)

        layer_control_layout.addWidget(self.current_layer_label)
        layer_control_layout.addWidget(self.layer_slider)
        layer_control_layout.addLayout(layer_nav_layout)

        layout.addWidget(layer_control_group)

        display_group = QGroupBox("Настройки отображения")
        display_layout = QGridLayout()
        display_group.setLayout(display_layout)

        self.animation_speed_label = QLabel("Скорость анимации:")
        self.animation_speed_slider = QSlider(Qt.Horizontal)
        self.animation_speed_slider.setRange(1, 100)
        self.animation_speed_slider.setValue(50)

        self.layer_height_label = QLabel("Высота слоя: 0.2 мм")

        display_layout.addWidget(self.animation_speed_label, 0, 0)
        display_layout.addWidget(self.animation_speed_slider, 0, 1)
        display_layout.addWidget(self.layer_height_label, 1, 0, 1, 2)

        layout.addWidget(display_group)

        layout.addStretch()
        return widget


    def connect_signals(self):
        self.load_file_btn.clicked.connect(self.load_file)
        self.reload_file_btn.clicked.connect(self.reload_file)

        self.line_numbers_checkbox.toggled.connect(self.update_line_numbers_visibility)
        self.highlight_moves_checkbox.toggled.connect(self.update_preview)
        self.filter_comments_checkbox.toggled.connect(self.update_preview)
        self.syntax_highlight_checkbox.toggled.connect(self.toggle_syntax_highlight)

        self.start_print_btn.clicked.connect(self.start_print)
        self.pause_print_btn.clicked.connect(self.pause_print)
        self.resume_print_btn.clicked.connect(self.resume_print)
        self.stop_print_btn.clicked.connect(self.stop_print)

        self.first_layer_btn.clicked.connect(lambda: self.set_layer(0))
        self.prev_layer_btn.clicked.connect(self.prev_layer)
        self.next_layer_btn.clicked.connect(self.next_layer)
        self.last_layer_btn.clicked.connect(self.last_layer)

        if self.gcode_handler:
            self.gcode_handler.print_progress.connect(self.update_print_progress)
            self.gcode_handler.print_status_changed.connect(self.update_print_status)
            self.gcode_handler.gcode_loaded.connect(self.on_gcode_loaded)


    def update_line_numbers_visibility(self, visible):
        self.line_number_area.setVisible(visible)
        self.update_line_number_area_width(0)


    def toggle_syntax_highlight(self, enabled):
        if enabled:
            self.highlighter = GCodeHighlighter(self.gcode_text.document())
        else:
            self.highlighter = None
            self.gcode_text.document().setHighlighter(None)


    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить файл G-кода",
            "",
            "G-code Files (*.gcode *.g *.nc);;All Files (*)"
        )

        if filename:
            self.load_gcode_file(filename)


    def reload_file(self):
        if self.current_file:
            self.load_gcode_file(self.current_file)


    def load_gcode_file(self, filename):
        try:
            self.gcode_commands = self.gcode_handler.load_gcode_file(filename)

            self.current_file = filename
            self.file_label.setText(f"Загружен: {os.path.basename(filename)}")
            self.file_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; }")

            self.reload_file_btn.setEnabled(True)
            self.update_controls()
            self.file_loaded.emit(filename)

        except Exception as e:
            self.file_label.setText(f"Ошибка загрузки: {str(e)}")
            self.file_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; }")


    def on_gcode_loaded(self, path_data, layers_data):
        self.layers_data = layers_data
        self.update_analysis_display(path_data, layers_data)
        self.update_layers_list()
        self.update_preview()


    def update_analysis_display(self, path_data, layers_data):
        if not layers_data:
            return

        total_lines = len(self.gcode_commands)
        layer_count = len(layers_data)

        print_moves = 0
        travel_moves = 0
        retractions = 0

        for layer in layers_data:
            for path in layer.get('paths', []):
                if path['type'] == 'print':
                    print_moves += len(path['points'])
                elif path['type'] == 'travel':
                    travel_moves += len(path['points'])
                elif path['type'] == 'retraction':
                    retractions += len(path['points'])

        self.total_lines_label.setText(str(total_lines))
        self.layer_count_label.setText(str(layer_count))
        self.print_moves_label.setText(str(print_moves))
        self.travel_moves_label.setText(str(travel_moves))
        self.retractions_label.setText(str(retractions))

        if layer_count > 0:
            self.layer_slider.setRange(0, layer_count - 1)
            self.current_layer_label.setText(f"Слой: 0 / {layer_count - 1}")


    def update_layers_list(self):
        self.layers_list.clear()

        for i, layer_data in enumerate(self.layers_data):
            z_height = layer_data.get('z', 0)
            paths_count = len(layer_data.get('paths', []))

            item_text = f"Слой {i}: Z={z_height:.2f} мм ({paths_count} путей)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.layers_list.addItem(item)


    def update_preview(self):
        if not self.gcode_commands:
            return

        content = []
        for cmd in self.gcode_commands:
            line = cmd['original']
            if not self.filter_comments_checkbox.isChecked() or not line.startswith(';'):
                content.append(line)

        self.gcode_text.setPlainText('\n'.join(content))
        self.goto_line_input.setRange(1, len(content))


    def goto_line(self):
        line_number = self.goto_line_input.value() - 1
        cursor = self.gcode_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        for _ in range(line_number):
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        self.gcode_text.setTextCursor(cursor)
        self.gcode_text.ensureCursorVisible()


    def find_text(self):
        search_text = self.find_input.text()
        if search_text:
            self.gcode_text.find(search_text)


    def on_layer_selected(self, item):
        layer_index = item.data(Qt.ItemDataRole.UserRole)
        if layer_index is not None:
            self.set_layer(layer_index)

            layer_data = self.layers_data[layer_index]
            z_height = layer_data.get('z', 0)
            paths_count = len(layer_data.get('paths', []))

            self.layer_info_label.setText(
                f"Слой {layer_index}: Z={z_height:.2f} мм, Путей: {paths_count}"
            )


    def on_layer_slider_changed(self, value):
        self.set_layer(value)


    def set_layer(self, layer_index):
        if 0 <= layer_index < len(self.layers_data):
            self.layer_slider.setValue(layer_index)
            self.current_layer_label.setText(f"Слой: {layer_index} / {len(self.layers_data) - 1}")
            self.layer_selected.emit(layer_index)


    def prev_layer(self):
        current = self.layer_slider.value()
        if current > 0:
            self.set_layer(current - 1)


    def next_layer(self):
        current = self.layer_slider.value()
        if current < self.layer_slider.maximum():
            self.set_layer(current + 1)


    def last_layer(self):
        self.set_layer(self.layer_slider.maximum())


    def start_print(self):
        if self.gcode_commands:
            self.gcode_handler.start_print(self.gcode_commands)
            self.print_started.emit()


    def pause_print(self):
        self.gcode_handler.pause_print()


    def resume_print(self):
        self.gcode_handler.resume_print()


    def stop_print(self):
        self.gcode_handler.stop_print()


    def update_print_progress(self, progress):
        self.print_progress.setValue(progress)


    def update_print_status(self, status):
        status_text = {
            'printing': 'Печать...',
            'paused': 'Пауза',
            'stopped': 'Остановлено',
            'finished': 'Завершено'
        }.get(status, status)

        self.progress_label.setText(status_text)


    def update_controls(self):
        has_file = bool(self.gcode_commands)
        self.start_print_btn.setEnabled(has_file)

        if has_file:
            self.file_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; }")
        else:
            self.file_label.setStyleSheet("QLabel { color: #888888; font-style: italic; }")