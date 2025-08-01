import sys
import math
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QCheckBox, QSpinBox, QGroupBox,
                             QGridLayout, QFrame, QSplitter, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import QMouseEvent, QWheelEvent, QPainter, QPen, QBrush, QColor
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *


class Advanced3DVisualization(QOpenGLWidget):
    position_clicked = pyqtSignal(float, float, float)
    layer_changed = pyqtSignal(int)

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager

        self.print_head_pos = [0.0, 0.0, 0.0]  # [X, Y, Z]

        self.build_volume = [
            self.config_manager.get("printer.build_volume.x", 220),
            self.config_manager.get("printer.build_volume.y", 220),
            self.config_manager.get("printer.build_volume.z", 250)
        ]

        self.camera_distance = 500.0
        self.camera_rotation_x = 30.0
        self.camera_rotation_y = 45.0
        self.camera_target = [self.build_volume[0] / 2, self.build_volume[1] / 2, self.build_volume[2] / 2]
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5
        self.zoom_sensitivity = 20.0

        self.grid_enabled = self.config_manager.get("ui.show_grid", True)
        self.axes_enabled = self.config_manager.get("ui.show_axes", True)
        self.build_plate_enabled = self.config_manager.get("ui.show_build_plate", True)

        self.gcode_path = []
        self.gcode_layers = []
        self.current_layer = 0
        self.max_layer = 0
        self.show_layers = self.config_manager.get("ui.show_layers", True)
        self.show_travel_moves = True
        self.show_print_moves = True
        self.show_retractions = True

        # Печатная головка и след
        self.print_head_trail = []
        self.max_trail_length = 2000

        # Анимация
        self.lighting_enabled = self.config_manager.get("ui.lighting_enabled", True)
        self.smooth_movement = self.config_manager.get("ui.smooth_movement", True)
        self.target_pos = [0.0, 0.0, 0.0]
        self.animation_speed = self.config_manager.get("gcode.animation_speed", 0.1)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(16)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_LIGHT1)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            # Основной свет
            light0_pos = [1.0, 1.0, 1.0, 0.0]
            light0_ambient = [0.3, 0.3, 0.3, 1.0]
            light0_diffuse = [0.8, 0.8, 0.8, 1.0]
            light0_specular = [1.0, 1.0, 1.0, 1.0]

            glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
            glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)

            # Дополнительный свет
            light1_pos = [-1.0, -1.0, 1.0, 0.0]
            light1_ambient = [0.1, 0.1, 0.1, 1.0]
            light1_diffuse = [0.4, 0.4, 0.4, 1.0]

            glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
            glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
            glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glShadeModel(GL_SMOOTH)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect_ratio = width / height
        gluPerspective(45.0, aspect_ratio, 1.0, 3000.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.setup_camera()

        # Отрисовка в правильном порядке
        if self.axes_enabled:
            self.draw_axes()

        if self.build_plate_enabled:
            self.draw_build_plate()

        self.draw_build_volume()

        if self.grid_enabled:
            self.draw_grid()

        # G-code визуализация
        if self.gcode_path and self.show_layers:
            self.draw_gcode_path()

        # Печатная головка и след
        self.draw_print_head_trail()
        self.draw_print_head()

        # UI overlay
        self.draw_ui_overlay()

    def setup_camera(self):
        """Исправленная настройка камеры с правильными осями"""
        rad_x = math.radians(self.camera_rotation_x)
        rad_y = math.radians(self.camera_rotation_y)

        # Правильное вычисление позиции камеры
        cam_x = self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
        cam_y = self.camera_distance * math.cos(rad_x) * math.cos(rad_y)  # Исправлено
        cam_z = self.camera_distance * math.sin(rad_x)  # Исправлено

        gluLookAt(
            cam_x + self.camera_target[0], cam_y + self.camera_target[1], cam_z + self.camera_target[2],
            self.camera_target[0], self.camera_target[1], self.camera_target[2],
            0.0, 0.0, 1.0  # Исправлено: Z - вверх
        )

    def draw_axes(self):
        """Отрисовка осей координат с правильными цветами и направлениями"""
        glDisable(GL_LIGHTING)
        glLineWidth(4.0)
        glBegin(GL_LINES)

        # X-ось (красная) - горизонтально вправо
        glColor3f(1.0, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(60.0, 0.0, 0.0)

        # Y-ось (зеленая) - горизонтально вглубь
        glColor3f(0.2, 1.0, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 60.0, 0.0)

        # Z-ось (синяя) - вертикально вверх
        glColor3f(0.2, 0.2, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 60.0)

        glEnd()
        glLineWidth(1.0)

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_build_plate(self):
        """Отрисовка платформы печати в плоскости XY (Z=0)"""
        glDisable(GL_LIGHTING)
        glColor4f(0.4, 0.4, 0.4, 0.9)

        glBegin(GL_QUADS)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, 0.0)
        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)
        glVertex3f(0.0, self.build_volume[1], 0.0)
        glEnd()

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_build_volume(self):
        """Отрисовка границ области печати"""
        glDisable(GL_LIGHTING)
        glColor4f(0.6, 0.6, 0.6, 0.4)
        glLineWidth(2.0)

        glBegin(GL_LINES)

        # Нижний прямоугольник (Z=0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, 0.0)

        glVertex3f(self.build_volume[0], 0.0, 0.0)
        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)

        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)
        glVertex3f(0.0, self.build_volume[1], 0.0)

        glVertex3f(0.0, self.build_volume[1], 0.0)
        glVertex3f(0.0, 0.0, 0.0)

        # Верхний прямоугольник (Z=max)
        glVertex3f(0.0, 0.0, self.build_volume[2])
        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])

        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])
        glVertex3f(self.build_volume[0], self.build_volume[1], self.build_volume[2])

        glVertex3f(self.build_volume[0], self.build_volume[1], self.build_volume[2])
        glVertex3f(0.0, self.build_volume[1], self.build_volume[2])

        glVertex3f(0.0, self.build_volume[1], self.build_volume[2])
        glVertex3f(0.0, 0.0, self.build_volume[2])

        # Вертикальные линии
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, self.build_volume[2])

        glVertex3f(self.build_volume[0], 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])

        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)
        glVertex3f(self.build_volume[0], self.build_volume[1], self.build_volume[2])

        glVertex3f(0.0, self.build_volume[1], 0.0)
        glVertex3f(0.0, self.build_volume[1], self.build_volume[2])

        glEnd()
        glLineWidth(1.0)

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_grid(self):
        """Отрисовка сетки на платформе печати"""
        glDisable(GL_LIGHTING)
        glColor4f(0.5, 0.5, 0.5, 0.6)
        glLineWidth(1.0)

        grid_spacing = 10.0
        glBegin(GL_LINES)

        # Линии по X (параллельные оси Y)
        x = 0.0
        while x <= self.build_volume[0]:
            glVertex3f(x, 0.0, 0.0)
            glVertex3f(x, self.build_volume[1], 0.0)
            x += grid_spacing

        # Линии по Y (параллельные оси X)
        y = 0.0
        while y <= self.build_volume[1]:
            glVertex3f(0.0, y, 0.0)
            glVertex3f(self.build_volume[0], y, 0.0)
            y += grid_spacing

        glEnd()

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_gcode_path(self):
        """Улучшенная отрисовка G-code пути с различными типами движений"""
        if not self.gcode_path:
            return

        glDisable(GL_LIGHTING)

        # Отрисовка путей по слоям
        for layer_idx, layer_data in enumerate(self.gcode_layers):
            if layer_idx > self.current_layer and self.current_layer >= 0:
                continue

            # Настройка прозрачности для разных слоев
            if layer_idx == self.current_layer:
                alpha = 1.0
            elif layer_idx < self.current_layer:
                alpha = 0.3
            else:
                alpha = 0.1

            for path_segment in layer_data.get('paths', []):
                path_type = path_segment.get('type', 'print')
                points = path_segment.get('points', [])

                if not points:
                    continue

                # Выбор цвета и толщины линии в зависимости от типа движения
                if path_type == 'print' and self.show_print_moves:
                    glColor4f(0.0, 1.0, 0.2, alpha)  # Зеленый для печати
                    glLineWidth(3.0)
                elif path_type == 'travel' and self.show_travel_moves:
                    glColor4f(0.0, 0.5, 1.0, alpha * 0.5)  # Синий для перемещений
                    glLineWidth(1.0)
                elif path_type == 'retraction' and self.show_retractions:
                    glColor4f(1.0, 0.5, 0.0, alpha)  # Оранжевый для ретрактов
                    glLineWidth(2.0)
                else:
                    continue

                # Отрисовка сегмента пути
                glBegin(GL_LINE_STRIP)
                for point in points:
                    glVertex3f(point[0], point[1], point[2])
                glEnd()

        glLineWidth(1.0)
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_print_head_trail(self):
        """Отрисовка следа печатной головки"""
        if len(self.print_head_trail) < 2:
            return

        glDisable(GL_LIGHTING)
        glLineWidth(4.0)
        glBegin(GL_LINE_STRIP)

        for i, pos in enumerate(self.print_head_trail):
            alpha = (i / len(self.print_head_trail)) * 0.8
            glColor4f(1.0, 0.3, 0.0, alpha)
            glVertex3f(pos[0], pos[1], pos[2])

        glEnd()
        glLineWidth(1.0)
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_print_head(self):
        """Отрисовка печатной головки"""
        glPushMatrix()
        glTranslatef(self.print_head_pos[0], self.print_head_pos[1], self.print_head_pos[2])

        if self.lighting_enabled:
            glColor3f(0.9, 0.1, 0.1)
        else:
            glColor3f(1.0, 0.0, 0.0)

        # Сфера для головки
        self.draw_sphere(5.0, 20, 20)

        # Цилиндр для сопла
        glColor3f(0.3, 0.3, 0.3)
        glTranslatef(0.0, 0.0, -10.0)
        self.draw_cylinder(2.0, 10.0, 12)

        glPopMatrix()

    def draw_sphere(self, radius, slices, stacks):
        """Отрисовка сферы"""
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)

            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)

            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)

                if self.lighting_enabled:
                    glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                if self.lighting_enabled:
                    glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()

    def draw_cylinder(self, radius, height, slices):
        """Отрисовка цилиндра"""
        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            if self.lighting_enabled:
                glNormal3f(x, y, 0.0)
            glVertex3f(x, y, 0.0)
            glVertex3f(x, y, height)
        glEnd()

    def draw_ui_overlay(self):
        """Отрисовка информационного оверлея"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(255, 255, 255))

        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        x, y, z = self.print_head_pos
        distance = self.camera_distance
        rot_x = self.camera_rotation_x
        rot_y = self.camera_rotation_y

        lines = [
            f"Позиция X: {x:.1f} мм",
            f"Позиция Y: {y:.1f} мм",
            f"Позиция Z: {z:.1f} мм",
            f"Камера: {distance:.0f} мм",
            f"Поворот X: {rot_x:.1f}°",
            f"Поворот Y: {rot_y:.1f}°",
            f"Слой: {self.current_layer} / {self.max_layer}"
        ]

        margin = 10
        for i, text in enumerate(lines):
            painter.drawText(margin, margin + 20 * (i + 1), text)

        painter.end()

    def animate(self):
        """Анимация плавного движения"""
        if self.smooth_movement:
            for i in range(3):
                diff = self.target_pos[i] - self.print_head_pos[i]
                if abs(diff) > 0.1:
                    self.print_head_pos[i] += diff * self.animation_speed

        self.update()

    def update_position(self, x, y, z):
        """Обновление позиции печатной головки"""
        if self.smooth_movement:
            self.target_pos = [x, y, z]
        else:
            self.print_head_pos = [x, y, z]

        self.print_head_trail.append([x, y, z])
        if len(self.print_head_trail) > self.max_trail_length:
            self.print_head_trail.pop(0)

        self.update()

    def clear_trail(self):
        """Очистка следа печатной головки"""
        self.print_head_trail.clear()
        self.update()

    def set_build_volume(self, x, y, z):
        """Установка размеров области печати"""
        self.build_volume = [x, y, z]
        self.camera_target = [x / 2, y / 2, z / 2]
        self.update()

    def load_gcode_path(self, path_data, layers_data=None):
        """Загрузка G-code пути с поддержкой слоев"""
        self.gcode_path = path_data
        if layers_data:
            self.gcode_layers = layers_data
            self.max_layer = len(layers_data) - 1
        else:
            self.gcode_layers = []
            self.max_layer = 0
        self.current_layer = 0
        self.update()

    def set_current_layer(self, layer):
        """Установка текущего слоя"""
        self.current_layer = max(0, min(layer, self.max_layer))
        self.layer_changed.emit(self.current_layer)
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши"""
        self.last_mouse_pos = event.position()

        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.handle_position_click(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Исправленная обработка движения мыши для управления камерой"""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.position()
            return

        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()

        if event.buttons() & Qt.MouseButton.RightButton:
            # Вращение камеры
            self.camera_rotation_y += dx * self.mouse_sensitivity
            self.camera_rotation_x -= dy * self.mouse_sensitivity  # Исправлено направление

            # Ограничение углов
            self.camera_rotation_x = max(-89, min(89, self.camera_rotation_x))
            self.camera_rotation_y = self.camera_rotation_y % 360

            self.update()
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            # Панорамирование
            move_speed = self.camera_distance * 0.001

            # Исправленное панорамирование с учетом поворота камеры
            rad_y = math.radians(self.camera_rotation_y)

            # Движение в плоскости XY
            self.camera_target[0] -= (dx * math.cos(rad_y) + dy * math.sin(rad_y)) * move_speed
            self.camera_target[1] -= (-dx * math.sin(rad_y) + dy * math.cos(rad_y)) * move_speed

            self.update()

        self.last_mouse_pos = event.position()

    def wheelEvent(self, event: QWheelEvent):
        """Обработка колеса мыши для масштабирования"""
        delta = event.angleDelta().y()
        zoom_factor = 1.0 + (delta / 1200.0)

        self.camera_distance /= zoom_factor
        self.camera_distance = max(50.0, min(2000.0, self.camera_distance))

        self.update()

    def handle_position_click(self, event):
        """Обработка клика для установки позиции"""
        # Упрощенная версия - требует доработки для точного позиционирования
        x = event.position().x()
        y = event.position().y()

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        # Примерное преобразование экранных координат в мировые
        norm_x = (x / width) * self.build_volume[0]
        norm_y = ((height - y) / height) * self.build_volume[1]
        norm_z = self.print_head_pos[2]  # Сохраняем текущую высоту

        self.position_clicked.emit(norm_x, norm_y, norm_z)

    def toggle_grid(self):
        """Переключение отображения сетки"""
        self.grid_enabled = not self.grid_enabled
        self.update()

    def toggle_axes(self):
        """Переключение отображения осей"""
        self.axes_enabled = not self.axes_enabled
        self.update()

    def toggle_build_plate(self):
        """Переключение отображения платформы"""
        self.build_plate_enabled = not self.build_plate_enabled
        self.update()

    def toggle_lighting(self):
        """Переключение освещения"""
        self.lighting_enabled = not self.lighting_enabled
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        self.update()

    def toggle_smooth_movement(self):
        """Переключение плавного движения"""
        self.smooth_movement = not self.smooth_movement

    def toggle_travel_moves(self):
        """Переключение отображения перемещений"""
        self.show_travel_moves = not self.show_travel_moves
        self.update()

    def toggle_print_moves(self):
        """Переключение отображения печати"""
        self.show_print_moves = not self.show_print_moves
        self.update()

    def toggle_retractions(self):
        """Переключение отображения ретрактов"""
        self.show_retractions = not self.show_retractions
        self.update()

    def reset_camera(self):
        """Сброс камеры в исходное положение"""
        self.camera_distance = 500.0
        self.camera_rotation_x = -30.0
        self.camera_rotation_y = 45.0
        self.camera_target = [self.build_volume[0] / 2, self.build_volume[1] / 2, self.build_volume[2] / 2]
        self.update()


class Advanced3DVisualizationWidget(QWidget):
    """Виджет с 3D визуализацией и элементами управления как в Simplify3D"""
    position_clicked = pyqtSignal(float, float, float)

    def __init__(self, config_manager):
        self.config_manager = config_manager
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Основной сплиттер
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 3D визуализация
        self.visualization = Advanced3DVisualization(self.config_manager)
        splitter.addWidget(self.visualization)

        # Панель управления
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)

        # Настройка размеров
        splitter.setSizes([800, 300])

        # Подключение сигналов
        self.visualization.position_clicked.connect(self.position_clicked)
        self.visualization.layer_changed.connect(self.on_layer_changed)

    def create_control_panel(self):
        """Создание панели управления как в Simplify3D"""
        panel = QWidget()
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Группа управления видом
        view_group = QGroupBox("Управление видом")
        view_layout = QGridLayout()
        view_group.setLayout(view_layout)

        # Чекбоксы для отображения элементов
        self.grid_checkbox = QCheckBox("Сетка")
        self.grid_checkbox.setChecked(self.visualization.grid_enabled)
        self.grid_checkbox.toggled.connect(self.visualization.toggle_grid)

        self.axes_checkbox = QCheckBox("Оси координат")
        self.axes_checkbox.setChecked(self.visualization.axes_enabled)
        self.axes_checkbox.toggled.connect(self.visualization.toggle_axes)

        self.build_plate_checkbox = QCheckBox("Платформа")
        self.build_plate_checkbox.setChecked(self.visualization.build_plate_enabled)
        self.build_plate_checkbox.toggled.connect(self.visualization.toggle_build_plate)

        self.lighting_checkbox = QCheckBox("Освещение")
        self.lighting_checkbox.setChecked(self.visualization.lighting_enabled)
        self.lighting_checkbox.toggled.connect(self.visualization.toggle_lighting)

        view_layout.addWidget(self.grid_checkbox, 0, 0)
        view_layout.addWidget(self.axes_checkbox, 0, 1)
        view_layout.addWidget(self.build_plate_checkbox, 1, 0)
        view_layout.addWidget(self.lighting_checkbox, 1, 1)

        layout.addWidget(view_group)

        # Группа G-code визуализации
        gcode_group = QGroupBox("G-code визуализация")
        gcode_layout = QGridLayout()
        gcode_group.setLayout(gcode_layout)

        self.print_moves_checkbox = QCheckBox("Печать")
        self.print_moves_checkbox.setChecked(True)
        self.print_moves_checkbox.toggled.connect(self.visualization.toggle_print_moves)

        self.travel_moves_checkbox = QCheckBox("Перемещения")
        self.travel_moves_checkbox.setChecked(True)
        self.travel_moves_checkbox.toggled.connect(self.visualization.toggle_travel_moves)

        self.retractions_checkbox = QCheckBox("Ретракты")
        self.retractions_checkbox.setChecked(True)
        self.retractions_checkbox.toggled.connect(self.visualization.toggle_retractions)

        gcode_layout.addWidget(self.print_moves_checkbox, 0, 0)
        gcode_layout.addWidget(self.travel_moves_checkbox, 0, 1)
        gcode_layout.addWidget(self.retractions_checkbox, 1, 0)

        layout.addWidget(gcode_group)

        # Группа управления слоями
        layer_group = QGroupBox("Управление слоями")
        layer_layout = QVBoxLayout()
        layer_group.setLayout(layer_layout)

        # Слайдер слоев
        self.layer_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_slider.setRange(0, 0)
        self.layer_slider.setValue(0)
        self.layer_slider.valueChanged.connect(self.visualization.set_current_layer)

        # Метка текущего слоя
        self.layer_label = QLabel("Слой: 0 / 0")
        self.layer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопки управления слоями
        layer_buttons_layout = QHBoxLayout()

        self.prev_layer_btn = QPushButton("◀")
        self.prev_layer_btn.setMaximumWidth(30)
        self.prev_layer_btn.clicked.connect(self.prev_layer)

        self.next_layer_btn = QPushButton("▶")
        self.next_layer_btn.setMaximumWidth(30)
        self.next_layer_btn.clicked.connect(self.next_layer)

        self.first_layer_btn = QPushButton("⏮")
        self.first_layer_btn.setMaximumWidth(30)
        self.first_layer_btn.clicked.connect(self.first_layer)

        self.last_layer_btn = QPushButton("⏭")
        self.last_layer_btn.setMaximumWidth(30)
        self.last_layer_btn.clicked.connect(self.last_layer)

        layer_buttons_layout.addWidget(self.first_layer_btn)
        layer_buttons_layout.addWidget(self.prev_layer_btn)
        layer_buttons_layout.addStretch()
        layer_buttons_layout.addWidget(self.next_layer_btn)
        layer_buttons_layout.addWidget(self.last_layer_btn)

        layer_layout.addWidget(self.layer_label)
        layer_layout.addWidget(self.layer_slider)
        layer_layout.addLayout(layer_buttons_layout)

        layout.addWidget(layer_group)

        # Группа управления камерой
        camera_group = QGroupBox("Управление камерой")
        camera_layout = QGridLayout()
        camera_group.setLayout(camera_layout)

        # Кнопки предустановленных видов
        self.view_front_btn = QPushButton("Спереди")
        self.view_front_btn.clicked.connect(self.view_front)

        self.view_back_btn = QPushButton("Сзади")
        self.view_back_btn.clicked.connect(self.view_back)

        self.view_left_btn = QPushButton("Слева")
        self.view_left_btn.clicked.connect(self.view_left)

        self.view_right_btn = QPushButton("Справа")
        self.view_right_btn.clicked.connect(self.view_right)

        self.view_top_btn = QPushButton("Сверху")
        self.view_top_btn.clicked.connect(self.view_top)

        self.view_bottom_btn = QPushButton("Снизу")
        self.view_bottom_btn.clicked.connect(self.view_bottom)

        camera_layout.addWidget(self.view_front_btn, 0, 0)
        camera_layout.addWidget(self.view_back_btn, 0, 1)
        camera_layout.addWidget(self.view_left_btn, 1, 0)
        camera_layout.addWidget(self.view_right_btn, 1, 1)
        camera_layout.addWidget(self.view_top_btn, 2, 0)
        camera_layout.addWidget(self.view_bottom_btn, 2, 1)

        # Кнопка сброса камеры
        self.reset_camera_btn = QPushButton("Сбросить вид")
        self.reset_camera_btn.clicked.connect(self.visualization.reset_camera)
        camera_layout.addWidget(self.reset_camera_btn, 3, 0, 1, 2)

        layout.addWidget(camera_group)

        # Группа информации
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)

        self.info_label = QLabel("Загрузите G-code файл для просмотра")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        layout.addWidget(info_group)

        layout.addStretch()

        return panel

    def on_layer_changed(self, layer):
        """Обработка изменения слоя"""
        self.layer_label.setText(f"Слой: {layer} / {self.visualization.max_layer}")
        self.layer_slider.setValue(layer)

    def prev_layer(self):
        """Предыдущий слой"""
        current = self.visualization.current_layer
        if current > 0:
            self.visualization.set_current_layer(current - 1)

    def next_layer(self):
        """Следующий слой"""
        current = self.visualization.current_layer
        if current < self.visualization.max_layer:
            self.visualization.set_current_layer(current + 1)

    def first_layer(self):
        """Первый слой"""
        self.visualization.set_current_layer(0)

    def last_layer(self):
        """Последний слой"""
        self.visualization.set_current_layer(self.visualization.max_layer)

    def view_front(self):
        """Вид спереди"""
        self.visualization.camera_rotation_x = 0
        self.visualization.camera_rotation_y = 0
        self.visualization.update()

    def view_back(self):
        """Вид сзади"""
        self.visualization.camera_rotation_x = 0
        self.visualization.camera_rotation_y = 180
        self.visualization.update()

    def view_left(self):
        """Вид слева"""
        self.visualization.camera_rotation_x = 0
        self.visualization.camera_rotation_y = -90
        self.visualization.update()

    def view_right(self):
        """Вид справа"""
        self.visualization.camera_rotation_x = 0
        self.visualization.camera_rotation_y = 90
        self.visualization.update()

    def view_top(self):
        """Вид сверху"""
        self.visualization.camera_rotation_x = -90
        self.visualization.camera_rotation_y = 0
        self.visualization.update()

    def view_bottom(self):
        """Вид снизу"""
        self.visualization.camera_rotation_x = 90
        self.visualization.camera_rotation_y = 0
        self.visualization.update()

    def update_position(self, x, y, z):
        """Обновление позиции печатной головки"""
        self.visualization.update_position(x, y, z)

    def load_gcode_path(self, path_data, layers_data=None):
        """Загрузка G-code пути"""
        self.visualization.load_gcode_path(path_data, layers_data)

        # Обновление информации
        if layers_data:
            layer_count = len(layers_data)
            self.layer_slider.setRange(0, layer_count - 1)
            self.info_label.setText(f"Загружено слоев: {layer_count}")
        else:
            self.info_label.setText("G-code загружен")

    def clear_trail(self):
        """Очистка следа печатной головки"""
        self.visualization.clear_trail()

