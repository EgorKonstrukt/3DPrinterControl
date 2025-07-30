import sys
import math
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QCheckBox, QSpinBox, QGroupBox,
                             QGridLayout, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import QMouseEvent, QWheelEvent, QPainter, QPen, QBrush, QColor
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

class Advanced3DVisualization(QOpenGLWidget):
    position_clicked = pyqtSignal(float, float, float)

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.print_head_pos = [0.0, 0.0, 0.0]
        self.build_volume = [self.config_manager.get("printer.build_volume.x"),
                             self.config_manager.get("printer.build_volume.y"),
                             self.config_manager.get("printer.build_volume.z")]
        print("Build volume:", self.build_volume)  # Add this in __init__

        self.camera_distance = 400.0
        self.camera_rotation_x = 25.0
        self.camera_rotation_y = 45.0
        self.camera_target = [110.0, 110.0, 125.0]
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.3
        self.zoom_sensitivity = 15.0

        self.grid_enabled = self.config_manager.get("ui.show_grid")
        self.axes_enabled = self.config_manager.get("ui.show_axes")
        self.build_plate_enabled = self.config_manager.get("ui.show_build_plate")
        self.print_head_trail = []
        self.max_trail_length = 2000
        self.gcode_path = []
        self.current_layer = 0
        self.show_layers =  self.config_manager.get("ui.show_layers")

        self.lighting_enabled = self.config_manager.get("ui.lighting_enabled")
        self.smooth_movement = self.config_manager.get("ui.smooth_movement")
        self.target_pos = [0.0, 0.0, 0.0]
        self.animation_speed = self.config_manager.get("gcode.animation_speed")

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

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_LIGHT1)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            light0_pos = [1.0, 1.0, 1.0, 0.0]
            light0_ambient = [0.2, 0.2, 0.2, 1.0]
            light0_diffuse = [0.8, 0.8, 0.8, 1.0]
            light0_specular = [1.0, 1.0, 1.0, 1.0]

            glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
            glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)

            light1_pos = [-1.0, -1.0, 1.0, 0.0]
            light1_ambient = [0.1, 0.1, 0.1, 1.0]
            light1_diffuse = [0.3, 0.3, 0.3, 1.0]

            glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
            glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
            glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

        glClearColor(0.05, 0.05, 0.05, 1.0)
        glShadeModel(GL_SMOOTH)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect_ratio = width / height
        gluPerspective(45.0, aspect_ratio, 1.0, 2000.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.setup_camera()

        if self.axes_enabled:
            self.draw_axes()

        if self.build_plate_enabled:
            self.draw_build_plate()

        self.draw_build_volume()

        if self.grid_enabled:
            self.draw_grid()

        if self.gcode_path and self.show_layers:
            self.draw_gcode_path()

        self.draw_print_head_trail()
        self.draw_print_head()

        self.draw_ui_overlay()

    def setup_camera(self):
        rad_x = math.radians(self.camera_rotation_x)
        rad_y = math.radians(self.camera_rotation_y)

        cam_x = self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
        cam_y = self.camera_distance * math.sin(rad_x)
        cam_z = self.camera_distance * math.cos(rad_x) * math.cos(rad_y)

        gluLookAt(cam_x + self.camera_target[0], cam_y + self.camera_target[1], cam_z + self.camera_target[2],
                  self.camera_target[0], self.camera_target[1], self.camera_target[2],
                  0.0, 1.0, 0.0)

    def draw_axes(self):
        glDisable(GL_LIGHTING)
        glLineWidth(4.0)
        glBegin(GL_LINES)

        glColor3f(1.0, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(60.0, 0.0, 0.0)

        glColor3f(0.2, 1.0, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 60.0, 0.0)

        glColor3f(0.2, 0.2, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 60.0)

        glEnd()

        self.draw_axis_labels()

        glLineWidth(1.0)
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_axis_labels(self):
        pass

    def draw_build_plate(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.3, 0.3, 0.3, 0.8)

        glBegin(GL_QUADS)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])
        glVertex3f(0.0, 0.0, self.build_volume[2])
        glEnd()

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_build_volume(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.6, 0.6, 0.6, 0.3)
        glLineWidth(2.0)

        glBegin(GL_LINES)

        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, 0.0)

        glVertex3f(self.build_volume[0], 0.0, 0.0)
        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])

        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])
        glVertex3f(0.0, 0.0, self.build_volume[2])

        glVertex3f(0.0, 0.0, self.build_volume[2])
        glVertex3f(0.0, 0.0, 0.0)

        glVertex3f(0.0, self.build_volume[1], 0.0)
        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)

        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)
        glVertex3f(self.build_volume[0], self.build_volume[1], self.build_volume[2])

        glVertex3f(self.build_volume[0], self.build_volume[1], self.build_volume[2])
        glVertex3f(0.0, self.build_volume[1], self.build_volume[2])

        glVertex3f(0.0, self.build_volume[1], self.build_volume[2])
        glVertex3f(0.0, self.build_volume[1], 0.0)

        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, self.build_volume[1], 0.0)

        glVertex3f(self.build_volume[0], 0.0, 0.0)
        glVertex3f(self.build_volume[0], self.build_volume[1], 0.0)

        glVertex3f(self.build_volume[0], 0.0, self.build_volume[2])
        glVertex3f(self.build_volume[0], self.build_volume[1], self.build_volume[2])

        glVertex3f(0.0, 0.0, self.build_volume[2])
        glVertex3f(0.0, self.build_volume[1], self.build_volume[2])

        glEnd()

        glLineWidth(1.0)
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.4, 0.4, 0.4, 0.6)
        glLineWidth(1.0)

        grid_spacing = 10.0
        glBegin(GL_LINES)

        z = 0.0
        while z <= self.build_volume[2]:
            glVertex3f(0.0, 0.0, z)
            glVertex3f(self.build_volume[0], 0.0, z)
            z += grid_spacing

        x = 0.0
        while x <= self.build_volume[0]:
            glVertex3f(x, 0.0, 0.0)
            glVertex3f(x, 0.0, self.build_volume[2])
            x += grid_spacing

        glEnd()

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_gcode_path(self):
        if not self.gcode_path:
            return

        glDisable(GL_LIGHTING)
        glLineWidth(2.0)

        glBegin(GL_LINE_STRIP)
        for i, point in enumerate(self.gcode_path):
            if i <= self.current_layer * 100:
                glColor4f(0.0, 1.0, 0.5, 0.8)
            else:
                glColor4f(0.5, 0.5, 0.5, 0.3)
            glVertex3f(point[0], point[1], point[2])
        glEnd()

        glLineWidth(1.0)
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

    def draw_print_head_trail(self):
        if len(self.print_head_trail) < 2:
            return

        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
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
        glPushMatrix()
        glTranslatef(self.print_head_pos[0], self.print_head_pos[1], self.print_head_pos[2])

        if self.lighting_enabled:
            glColor3f(0.9, 0.1, 0.1)
        else:
            glColor3f(1.0, 0.0, 0.0)

        self.draw_sphere(4.0, 20, 20)

        glColor3f(0.3, 0.3, 0.3)
        glTranslatef(0.0, -8.0, 0.0)
        self.draw_cylinder(2.0, 8.0, 12)

        glPopMatrix()

    def draw_sphere(self, radius, slices, stacks):
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
                glVertex3f(x * zr0, z0, y * zr0)
                if self.lighting_enabled:
                    glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, z1, y * zr1)
            glEnd()

    def draw_cylinder(self, radius, height, slices):
        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)

            if self.lighting_enabled:
                glNormal3f(x, 0.0, z)
            glVertex3f(x, 0.0, z)
            glVertex3f(x, height, z)
        glEnd()

    def draw_ui_overlay(self):
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
        layer = self.current_layer

        lines = [
            f"Голова X: {x:.1f} мм",
            f"Голова Y: {y:.1f} мм",
            f"Голова Z: {z:.1f} мм",
            f"Камера: {distance:.0f} мм",
            f"Угол X: {rot_x:.1f}°",
            f"Угол Y: {rot_y:.1f}°",
            f"Слой: {layer}"
        ]

        margin = 10
        for i, text in enumerate(lines):
            painter.drawText(margin, margin + 20 * (i + 1), text)

        painter.end()

    def animate(self):
        if self.smooth_movement:
            for i in range(3):
                diff = self.target_pos[i] - self.print_head_pos[i]
                if abs(diff) > 0.1:
                    self.print_head_pos[i] += diff * self.animation_speed

        self.update()

    def update_position(self, x, y, z):
        if self.smooth_movement:
            self.target_pos = [x, y, z]
        else:
            self.print_head_pos = [x, y, z]

        self.print_head_trail.append([x, y, z])
        if len(self.print_head_trail) > self.max_trail_length:
            self.print_head_trail.pop(0)

        self.update()

    def clear_trail(self):
        self.print_head_trail.clear()
        self.update()

    def set_build_volume(self, x, y, z):
        self.build_volume = [x, y, z]
        self.camera_target = [x/2, y/2, z/2]
        self.update()

    def load_gcode_path(self, path_data):
        self.gcode_path = path_data
        self.current_layer = 0
        self.update()

    def set_current_layer(self, layer):
        self.current_layer = layer
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        self.last_mouse_pos = event.position()

        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.handle_position_click(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.position()
            return

        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()

        if event.buttons() & Qt.MouseButton.RightButton:
            self.camera_rotation_y += dx * self.mouse_sensitivity
            self.camera_rotation_x += dy * self.mouse_sensitivity

            self.camera_rotation_x = max(-89, min(89, self.camera_rotation_x))

            self.update()
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            move_speed = self.camera_distance * 0.001
            self.camera_target[0] -= dx * move_speed
            self.camera_target[2] += dy * move_speed
            self.update()

        self.last_mouse_pos = event.position()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        self.camera_distance -= delta / 120.0 * self.zoom_sensitivity
        self.camera_distance = max(50.0, min(2000.0, self.camera_distance))
        self.update()

    def handle_position_click(self, event):
        x = event.position().x()
        y = event.position().y()

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        norm_x = (x / width) * self.build_volume[0]
        norm_z = ((height - y) / height) * self.build_volume[2]
        norm_y = self.print_head_pos[1]

        self.position_clicked.emit(norm_x, norm_y, norm_z)

    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.update()

    def toggle_axes(self):
        self.axes_enabled = not self.axes_enabled
        self.update()

    def toggle_build_plate(self):
        self.build_plate_enabled = not self.build_plate_enabled
        self.update()

    def toggle_lighting(self):
        self.lighting_enabled = not self.lighting_enabled
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        self.update()

    def toggle_smooth_movement(self):
        self.smooth_movement = not self.smooth_movement

    def reset_camera(self):
        self.camera_distance = 400.0
        self.camera_rotation_x = 25.0
        self.camera_rotation_y = 45.0
        self.camera_target = [self.build_volume[0]/2, self.build_volume[1]/2, self.build_volume[2]/2]
        self.update()

class Advanced3DVisualizationWidget(QWidget):
    position_clicked = pyqtSignal(float, float, float)

    def __init__(self, config_manager):
        self.config_manager = config_manager
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        self.visualization = Advanced3DVisualization(self.config_manager)
        splitter.addWidget(self.visualization)

        controls_widget = self.create_controls_panel()
        splitter.addWidget(controls_widget)

        self.load_settings_from_config()

        splitter.setSizes([800, 200])
        self.setLayout(main_layout)
        self.connect_signals()

    def load_settings_from_config(self):
        # Размеры платформы
        vol = self.config_manager.get("printer.build_volume")
        self.x_spinbox.setValue(vol.get("x", 220))
        self.y_spinbox.setValue(vol.get("y", 220))
        self.z_spinbox.setValue(vol.get("z", 250))

        # Отображение UI
        self.grid_checkbox.setChecked(self.config_manager.get("ui.show_grid", True))
        self.axes_checkbox.setChecked(self.config_manager.get("ui.show_axes", True))
        self.build_plate_checkbox.setChecked(self.config_manager.get("ui.show_build_plate", True))
        self.lighting_checkbox.setChecked(self.config_manager.get("ui.lighting_enabled", True))
        self.smooth_checkbox.setChecked(self.config_manager.get("ui.smooth_movement", True))

    def apply_build_volume(self):
        x = self.x_spinbox.value()
        y = self.y_spinbox.value()
        z = self.z_spinbox.value()
        self.visualization.set_build_volume(x, y, z)
        self.config_manager.set("printer.build_volume.x", x)
        self.config_manager.set("printer.build_volume.y", y)
        self.config_manager.set("printer.build_volume.z", z)
        self.config_manager.save_config()

    def create_controls_panel(self):
        controls_widget = QWidget()
        controls_widget.setMaximumWidth(250)
        layout = QVBoxLayout()

        view_group = QGroupBox("Вид")
        view_layout = QVBoxLayout()

        self.grid_checkbox = QCheckBox("Сетка")
        self.grid_checkbox.setChecked(True)
        self.axes_checkbox = QCheckBox("Оси")
        self.axes_checkbox.setChecked(True)
        self.build_plate_checkbox = QCheckBox("Стол")
        self.build_plate_checkbox.setChecked(True)
        self.lighting_checkbox = QCheckBox("Освещение")
        self.lighting_checkbox.setChecked(True)
        self.smooth_checkbox = QCheckBox("Плавное движение")
        self.smooth_checkbox.setChecked(True)

        view_layout.addWidget(self.grid_checkbox)
        view_layout.addWidget(self.axes_checkbox)
        view_layout.addWidget(self.build_plate_checkbox)
        view_layout.addWidget(self.lighting_checkbox)
        view_layout.addWidget(self.smooth_checkbox)

        view_group.setLayout(view_layout)
        layout.addWidget(view_group)

        camera_group = QGroupBox("Камера")
        camera_layout = QVBoxLayout()

        self.reset_camera_btn = QPushButton("Сброс камеры")
        self.clear_trail_btn = QPushButton("Очистить след")

        camera_layout.addWidget(self.reset_camera_btn)
        camera_layout.addWidget(self.clear_trail_btn)

        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)

        layer_group = QGroupBox("Слои")
        layer_layout = QVBoxLayout()

        self.layer_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_slider.setRange(0, 100)
        self.layer_slider.setValue(0)
        self.layer_label = QLabel("Слой: 0")

        layer_layout.addWidget(self.layer_label)
        layer_layout.addWidget(self.layer_slider)

        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)

        build_volume_group = QGroupBox("Размеры стола")
        build_volume_layout = QGridLayout()

        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(1, 5000)
        # self.x_spinbox.setValue(220)
        self.x_spinbox.setSuffix(" мм")

        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(1, 5000)
        # self.y_spinbox.setValue(220)
        self.y_spinbox.setSuffix(" мм")

        self.z_spinbox = QSpinBox()
        self.z_spinbox.setRange(1, 5000)
        # self.z_spinbox.setValue(250)
        self.z_spinbox.setSuffix(" мм")

        self.apply_volume_btn = QPushButton("Применить")

        build_volume_layout.addWidget(QLabel("X:"), 0, 0)
        build_volume_layout.addWidget(self.x_spinbox, 0, 1)
        build_volume_layout.addWidget(QLabel("Y:"), 1, 0)
        build_volume_layout.addWidget(self.y_spinbox, 1, 1)
        build_volume_layout.addWidget(QLabel("Z:"), 2, 0)
        build_volume_layout.addWidget(self.z_spinbox, 2, 1)
        build_volume_layout.addWidget(self.apply_volume_btn, 3, 0, 1, 2)

        build_volume_group.setLayout(build_volume_layout)
        layout.addWidget(build_volume_group)

        layout.addStretch()
        controls_widget.setLayout(layout)

        return controls_widget

    def connect_signals(self):
        self.grid_checkbox.toggled.connect(self.handle_toggle_grid)
        self.axes_checkbox.toggled.connect(self.handle_toggle_axes)
        self.build_plate_checkbox.toggled.connect(self.handle_toggle_build_plate)
        self.lighting_checkbox.toggled.connect(self.handle_toggle_lighting)
        self.smooth_checkbox.toggled.connect(self.handle_toggle_smooth)

        self.reset_camera_btn.clicked.connect(self.visualization.reset_camera)
        self.clear_trail_btn.clicked.connect(self.visualization.clear_trail)

        self.layer_slider.valueChanged.connect(self.update_layer)
        self.apply_volume_btn.clicked.connect(self.apply_build_volume)

        self.visualization.position_clicked.connect(self.position_clicked.emit)

    def handle_toggle_grid(self, checked):
        self.visualization.grid_enabled = checked
        self.config_manager.set("ui.show_grid", checked)
        self.visualization.update()

    def handle_toggle_axes(self, checked):
        self.visualization.axes_enabled = checked
        self.config_manager.set("ui.show_axes", checked)
        self.visualization.update()

    def handle_toggle_build_plate(self, checked):
        self.visualization.build_plate_enabled = checked
        self.config_manager.set("ui.show_build_plate", checked)
        self.visualization.update()

    def handle_toggle_lighting(self, checked):
        self.visualization.lighting_enabled = checked
        self.config_manager.set("ui.lighting_enabled", checked)
        self.visualization.update()

    def handle_toggle_smooth(self, checked):
        self.visualization.smooth_movement = checked
        self.config_manager.set("ui.smooth_movement", checked)
    def update_layer(self, value):
        self.layer_label.setText(f"Слой: {value}")
        self.visualization.set_current_layer(value)

    def apply_build_volume(self):
        x = self.x_spinbox.value()
        y = self.y_spinbox.value()
        z = self.z_spinbox.value()
        self.visualization.set_build_volume(x, y, z)

    def update_position(self, x, y, z):
        self.visualization.update_position(x, y, z)

    def load_gcode_path(self, path_data):
        self.visualization.load_gcode_path(path_data)
        if path_data:
            max_layers = len(path_data) // 100
            self.layer_slider.setRange(0, max_layers)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = Advanced3DVisualizationWidget()
    widget.show()

    sys.exit(app.exec())

