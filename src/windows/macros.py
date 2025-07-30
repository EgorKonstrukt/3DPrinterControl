import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QTextEdit, QListWidget, 
                             QListWidgetItem, QGroupBox, QGridLayout,
                             QMessageBox, QInputDialog, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MacroDialog(QDialog):
    def __init__(self, gcode_handler, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.gcode_handler = gcode_handler
        self.macros = {}
        self.macros_file = os.path.join(os.path.dirname(__file__), "..", "config", "macros.json")
        
        self.setWindowTitle("Макросы")
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.load_macros()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        self.setLayout(layout)
    
    def create_left_panel(self):
        widget = QGroupBox("Список макросов")
        layout = QVBoxLayout()
        
        self.macro_list = QListWidget()
        layout.addWidget(self.macro_list)
        
        buttons_layout = QVBoxLayout()
        
        self.add_macro_btn = QPushButton("Добавить")
        self.edit_macro_btn = QPushButton("Редактировать")
        self.delete_macro_btn = QPushButton("Удалить")
        self.execute_macro_btn = QPushButton("Выполнить")
        self.execute_macro_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        buttons_layout.addWidget(self.add_macro_btn)
        buttons_layout.addWidget(self.edit_macro_btn)
        buttons_layout.addWidget(self.delete_macro_btn)
        buttons_layout.addWidget(self.execute_macro_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        
        self.macro_list.itemSelectionChanged.connect(self.on_macro_selected)
        self.add_macro_btn.clicked.connect(self.add_macro)
        self.edit_macro_btn.clicked.connect(self.edit_macro)
        self.delete_macro_btn.clicked.connect(self.delete_macro)
        self.execute_macro_btn.clicked.connect(self.execute_macro)
        
        return widget
    
    def create_right_panel(self):
        widget = QGroupBox("Предпросмотр макроса")
        layout = QVBoxLayout()
        
        info_layout = QGridLayout()
        
        self.name_label = QLabel("Не выбран")
        self.description_label = QLabel("Не выбран")
        
        info_layout.addWidget(QLabel("Название:"), 0, 0)
        info_layout.addWidget(self.name_label, 0, 1)
        info_layout.addWidget(QLabel("Описание:"), 1, 0)
        info_layout.addWidget(self.description_label, 1, 1)
        
        layout.addLayout(info_layout)
        
        self.commands_text = QTextEdit()
        self.commands_text.setReadOnly(True)
        self.commands_text.setFont(QFont("Consolas", 9))
        self.commands_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
            }
        """)
        
        layout.addWidget(QLabel("Команды:"))
        layout.addWidget(self.commands_text)
        
        widget.setLayout(layout)
        return widget
    
    def load_macros(self):
        try:
            if os.path.exists(self.macros_file):
                with open(self.macros_file, 'r', encoding='utf-8') as f:
                    self.macros = json.load(f)
            else:
                self.create_default_macros()
            
            self.update_macro_list()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить макросы: {e}")
            self.create_default_macros()
    
    def create_default_macros(self):
        self.macros = {
            "Нагрев PLA": {
                "description": "Нагрев экструдера и стола для PLA",
                "commands": [
                    "M104 S200",
                    "M140 S60",
                    "M109 S200",
                    "M190 S60"
                ]
            },
            "Нагрев ABS": {
                "description": "Нагрев экструдера и стола для ABS",
                "commands": [
                    "M104 S240",
                    "M140 S80",
                    "M109 S240",
                    "M190 S80"
                ]
            },
            "Охлаждение": {
                "description": "Выключение всех нагревателей",
                "commands": [
                    "M104 S0",
                    "M140 S0",
                    "M106 S0"
                ]
            },
            "Подготовка к печати": {
                "description": "Стандартная подготовка принтера",
                "commands": [
                    "G28",
                    "G29",
                    "G1 Z5 F3000",
                    "G1 X10 Y10 F3000"
                ]
            },
            "Завершение печати": {
                "description": "Процедуры после печати",
                "commands": [
                    "M104 S0",
                    "M140 S0",
                    "M106 S0",
                    "G91",
                    "G1 Z10 F3000",
                    "G90",
                    "G1 X0 Y200 F3000",
                    "M84"
                ]
            }
        }
        self.save_macros()
    
    def save_macros(self):
        try:
            os.makedirs(os.path.dirname(self.macros_file), exist_ok=True)
            with open(self.macros_file, 'w', encoding='utf-8') as f:
                json.dump(self.macros, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить макросы: {e}")
    
    def update_macro_list(self):
        self.macro_list.clear()
        for name in self.macros.keys():
            item = QListWidgetItem(name)
            self.macro_list.addItem(item)
    
    def on_macro_selected(self):
        current_item = self.macro_list.currentItem()
        if current_item:
            name = current_item.text()
            macro = self.macros.get(name, {})
            
            self.name_label.setText(name)
            self.description_label.setText(macro.get("description", "Нет описания"))
            
            commands_text = "\n".join(macro.get("commands", []))
            self.commands_text.setText(commands_text)
        else:
            self.name_label.setText("Не выбран")
            self.description_label.setText("Не выбран")
            self.commands_text.clear()
    
    def add_macro(self):
        dialog = MacroEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, description, commands = dialog.get_macro_data()
            if name and name not in self.macros:
                self.macros[name] = {
                    "description": description,
                    "commands": commands
                }
                self.save_macros()
                self.update_macro_list()
            elif name in self.macros:
                QMessageBox.warning(self, "Ошибка", "Макрос с таким именем уже существует")
    
    def edit_macro(self):
        current_item = self.macro_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Информация", "Выберите макрос для редактирования")
            return
        
        name = current_item.text()
        macro = self.macros[name]
        
        dialog = MacroEditDialog(self, name, macro["description"], macro["commands"])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, description, commands = dialog.get_macro_data()
            if new_name:
                if new_name != name:
                    del self.macros[name]
                
                self.macros[new_name] = {
                    "description": description,
                    "commands": commands
                }
                self.save_macros()
                self.update_macro_list()
    
    def delete_macro(self):
        current_item = self.macro_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Информация", "Выберите макрос для удаления")
            return
        
        name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить макрос '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.macros[name]
            self.save_macros()
            self.update_macro_list()
    
    def execute_macro(self):
        current_item = self.macro_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Информация", "Выберите макрос для выполнения")
            return
        
        name = current_item.text()
        macro = self.macros[name]
        commands = macro.get("commands", [])
        
        if not commands:
            QMessageBox.warning(self, "Ошибка", "Макрос не содержит команд")
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Выполнить макрос '{name}'?\n\nКоманды:\n" + "\n".join(commands),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for command in commands:
                if command.strip():
                    self.gcode_handler.send_command(command.strip())
            
            QMessageBox.information(self, "Выполнено", f"Макрос '{name}' отправлен на выполнение")

class MacroEditDialog(QDialog):
    def __init__(self, parent=None, name="", description="", commands=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование макроса")
        self.setMinimumSize(400, 300)
        
        if commands is None:
            commands = []
        
        self.init_ui(name, description, commands)
    
    def init_ui(self, name, description, commands):
        layout = QVBoxLayout()
        
        form_layout = QGridLayout()
        
        self.name_edit = QLineEdit(name)
        self.description_edit = QLineEdit(description)
        
        form_layout.addWidget(QLabel("Название:"), 0, 0)
        form_layout.addWidget(self.name_edit, 0, 1)
        form_layout.addWidget(QLabel("Описание:"), 1, 0)
        form_layout.addWidget(self.description_edit, 1, 1)
        
        layout.addLayout(form_layout)
        
        layout.addWidget(QLabel("Команды (по одной на строку):"))
        
        self.commands_edit = QTextEdit()
        self.commands_edit.setFont(QFont("Consolas", 9))
        self.commands_edit.setText("\n".join(commands))
        
        layout.addWidget(self.commands_edit)
        
        buttons_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Отмена")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_macro_data(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        commands_text = self.commands_edit.toPlainText().strip()
        commands = [cmd.strip() for cmd in commands_text.split('\n') if cmd.strip()]
        
        return name, description, commands

