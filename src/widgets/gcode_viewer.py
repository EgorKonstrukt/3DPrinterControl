import os
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTextEdit, QProgressBar, QFileDialog,
                             QGroupBox, QGridLayout, QSpinBox, QCheckBox,
                             QTabWidget, QListWidget, QListWidgetItem,
                             QSplitter, QFrame, QSlider, QComboBox, QLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class GCodeViewer(QWidget):
    """Улучшенный просмотрщик G-code с полноценным отображением как в Simplify3D"""

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

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
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

        layout.addWidget(file_group)

        # Основной сплиттер
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)

        # Левая панель - вкладки
        left_panel = QTabWidget()
        main_splitter.addWidget(left_panel)

        # Вкладка предпросмотра
        preview_tab = self.create_preview_tab()
        left_panel.addTab(preview_tab, "Код")

        # Вкладка анализа
        analysis_tab = self.create_analysis_tab()
        left_panel.addTab(analysis_tab, "Анализ")

        # Вкладка слоев
        layers_tab = self.create_layers_tab()
        left_panel.addTab(layers_tab, "Слои")

        # Правая панель - управление
        right_panel = self.create_control_panel()
        main_splitter.addWidget(right_panel)

        # Настройка размеров
        main_splitter.setSizes([600, 300])

    def create_preview_tab(self):
        """Создание вкладки предпросмотра кода"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Панель управления отображением
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

        # Текстовое поле с кодом
        self.gcode_text = QTextEdit()
        self.gcode_text.setReadOnly(True)
        self.gcode_text.setFont(QFont("Consolas", 10))
        self.gcode_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #3399ff;
                line-height: 1.2;
            }
        """)

        layout.addWidget(self.gcode_text)

        # Панель навигации
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

    def create_analysis_tab(self):
        """Создание вкладки анализа"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Основная информация
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

        # Температуры
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

        # Размеры модели
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

        # Статистика движений
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
        """Создание вкладки управления слоями"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Список слоев
        layers_group = QGroupBox("Слои модели")
        layers_layout = QVBoxLayout()
        layers_group.setLayout(layers_layout)

        self.layers_list = QListWidget()
        self.layers_list.itemClicked.connect(self.on_layer_selected)
        layers_layout.addWidget(self.layers_list)

        # Информация о выбранном слое
        layer_info_layout = QHBoxLayout()

        self.layer_info_label = QLabel("Выберите слой для просмотра информации")
        layer_info_layout.addWidget(self.layer_info_label)

        layers_layout.addLayout(layer_info_layout)

        layout.addWidget(layers_group)

        # Фильтры отображения
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
        """Создание панели управления печатью"""
        widget = QWidget()
        widget.setMaximumWidth(300)
        widget.setMinimumWidth(250)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Управление печатью
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

        # Прогресс печати
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
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("QLabel { font-weight: bold; }")

        self.time_remaining_label = QLabel("Время: --:--")
        self.time_remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.print_progress)
        progress_layout.addWidget(self.time_remaining_label)

        layout.addWidget(progress_group)

        # Управление слоями
        layer_control_group = QGroupBox("Навигация по слоям")
        layer_control_layout = QVBoxLayout()
        layer_control_group.setLayout(layer_control_layout)

        # Слайдер слоев
        self.layer_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_slider.setRange(0, 0)
        self.layer_slider.setValue(0)
        self.layer_slider.valueChanged.connect(self.on_layer_slider_changed)

        self.current_layer_label = QLabel("Слой: 0 / 0")
        self.current_layer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_layer_label.setStyleSheet("QLabel { font-weight: bold; }")

        # Кнопки навигации
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

        # Настройки отображения
        display_group = QGroupBox("Настройки отображения")
        display_layout = QGridLayout()
        display_group.setLayout(display_layout)

        self.animation_speed_label = QLabel("Скорость анимации:")
        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
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
        """Подключение сигналов"""
        self.load_file_btn.clicked.connect(self.load_file)
        self.reload_file_btn.clicked.connect(self.reload_file)

        # Управление отображением
        self.line_numbers_checkbox.toggled.connect(self.update_preview)
        self.highlight_moves_checkbox.toggled.connect(self.update_preview)
        self.filter_comments_checkbox.toggled.connect(self.update_preview)
        self.syntax_highlight_checkbox.toggled.connect(self.update_preview)

        # Управление печатью
        self.start_print_btn.clicked.connect(self.start_print)
        self.pause_print_btn.clicked.connect(self.pause_print)
        self.resume_print_btn.clicked.connect(self.resume_print)
        self.stop_print_btn.clicked.connect(self.stop_print)

        # Навигация по слоям
        self.first_layer_btn.clicked.connect(lambda: self.set_layer(0))
        self.prev_layer_btn.clicked.connect(self.prev_layer)
        self.next_layer_btn.clicked.connect(self.next_layer)
        self.last_layer_btn.clicked.connect(self.last_layer)

        # Обработчики G-code
        if self.gcode_handler:
            self.gcode_handler.print_progress.connect(self.update_print_progress)
            self.gcode_handler.print_status_changed.connect(self.update_print_status)
            self.gcode_handler.gcode_loaded.connect(self.on_gcode_loaded)

    def load_file(self):
        """Загрузка файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить файл G-кода",
            "",
            "G-code Files (*.gcode *.g *.nc);;All Files (*)"
        )

        if filename:
            self.load_gcode_file(filename)

    def reload_file(self):
        """Перезагрузка текущего файла"""
        if self.current_file:
            self.load_gcode_file(self.current_file)

    def load_gcode_file(self, filename):
        """Загрузка и анализ G-code файла"""
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
        """Обработка загруженного G-code"""
        self.layers_data = layers_data
        self.update_analysis_display(path_data, layers_data)
        self.update_layers_list()
        self.update_preview()

    def update_analysis_display(self, path_data, layers_data):
        """Обновление отображения анализа"""
        if not layers_data:
            return

        # Подсчет статистики
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

        # Обновление меток
        self.total_lines_label.setText(str(total_lines))
        self.layer_count_label.setText(str(layer_count))
        self.print_moves_label.setText(str(print_moves))
        self.travel_moves_label.setText(str(travel_moves))
        self.retractions_label.setText(str(retractions))

        # Обновление слайдера слоев
        if layer_count > 0:
            self.layer_slider.setRange(0, layer_count - 1)
            self.current_layer_label.setText(f"Слой: 0 / {layer_count - 1}")

    def update_layers_list(self):
        """Обновление списка слоев"""
        self.layers_list.clear()

        for i, layer_data in enumerate(self.layers_data):
            z_height = layer_data.get('z', 0)
            paths_count = len(layer_data.get('paths', []))

            item_text = f"Слой {i}: Z={z_height:.2f} мм ({paths_count} путей)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.layers_list.addItem(item)

    def update_preview(self):
        """Обновление предпросмотра кода"""
        if not self.gcode_commands:
            return

        content = []
        line_num = 1

        for cmd in self.gcode_commands:
            line = cmd['original']

            # Фильтрация комментариев
            if self.filter_comments_checkbox.isChecked() and line.startswith(';'):
                continue

            # Добавление номеров строк
            if self.line_numbers_checkbox.isChecked():
                line = f"{line_num:4d}: {line}"
                line_num += 1

            content.append(line)

        self.gcode_text.setPlainText('\n'.join(content))

        # Обновление диапазона для перехода к строке
        self.goto_line_input.setRange(1, len(content))

    def goto_line(self):
        """Переход к строке"""
        line_number = self.goto_line_input.value() - 1
        cursor = self.gcode_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        for _ in range(line_number):
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        self.gcode_text.setTextCursor(cursor)
        self.gcode_text.ensureCursorVisible()

    def find_text(self):
        """Поиск текста"""
        search_text = self.find_input.text()
        if search_text:
            self.gcode_text.find(search_text)

    def on_layer_selected(self, item):
        """Обработка выбора слоя"""
        layer_index = item.data(Qt.ItemDataRole.UserRole)
        if layer_index is not None:
            self.set_layer(layer_index)

            # Обновление информации о слое
            layer_data = self.layers_data[layer_index]
            z_height = layer_data.get('z', 0)
            paths_count = len(layer_data.get('paths', []))

            self.layer_info_label.setText(
                f"Слой {layer_index}: Z={z_height:.2f} мм, Путей: {paths_count}"
            )

    def on_layer_slider_changed(self, value):
        """Обработка изменения слайдера слоев"""
        self.set_layer(value)

    def set_layer(self, layer_index):
        """Установка текущего слоя"""
        if 0 <= layer_index < len(self.layers_data):
            self.layer_slider.setValue(layer_index)
            self.current_layer_label.setText(f"Слой: {layer_index} / {len(self.layers_data) - 1}")
            self.layer_selected.emit(layer_index)

    def prev_layer(self):
        """Предыдущий слой"""
        current = self.layer_slider.value()
        if current > 0:
            self.set_layer(current - 1)

    def next_layer(self):
        """Следующий слой"""
        current = self.layer_slider.value()
        if current < self.layer_slider.maximum():
            self.set_layer(current + 1)

    def last_layer(self):
        """Последний слой"""
        self.set_layer(self.layer_slider.maximum())

    def start_print(self):
        """Начало печати"""
        if self.gcode_commands:
            self.gcode_handler.start_print(self.gcode_commands)
            self.print_started.emit()

    def pause_print(self):
        """Пауза печати"""
        self.gcode_handler.pause_print()

    def resume_print(self):
        """Возобновление печати"""
        self.gcode_handler.resume_print()

    def stop_print(self):
        """Остановка печати"""
        self.gcode_handler.stop_print()

    def update_print_progress(self, progress):
        """Обновление прогресса печати"""
        self.print_progress.setValue(progress)

    def update_print_status(self, status):
        """Обновление статуса печати"""
        status_text = {
            'printing': 'Печать...',
            'paused': 'Пауза',
            'stopped': 'Остановлено',
            'finished': 'Завершено'
        }.get(status, status)

        self.progress_label.setText(status_text)

    def update_controls(self):
        """Обновление состояния элементов управления"""
        has_file = bool(self.gcode_commands)
        self.start_print_btn.setEnabled(has_file)

        if has_file:
            self.file_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; }")
        else:
            self.file_label.setStyleSheet("QLabel { color: #888888; font-style: italic; }")


# Дополнительный импорт для поиска
from PyQt6.QtWidgets import QLineEdit

