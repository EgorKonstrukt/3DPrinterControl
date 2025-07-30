import re
import time
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class GCodeHandler(QObject):
    print_progress = pyqtSignal(int)
    print_status_changed = pyqtSignal(str)
    position_changed = pyqtSignal(float, float, float)
    temperature_changed = pyqtSignal(str, float, float)

    def __init__(self, serial_comm):
        super().__init__()
        self.serial_comm = serial_comm
        self.current_position = [0.0, 0.0, 0.0, 0.0]
        self.is_printing = False
        self.is_paused = False
        self.print_thread = None
        self.gcode_commands = []
        self.current_line = 0
        self.total_lines = 0

        self.temperatures = {
            'extruder': {'current': 0.0, 'target': 0.0},
            'bed': {'current': 0.0, 'target': 0.0}
        }

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.request_status)
        self.status_timer.start(2000)

        if self.serial_comm:
            self.serial_comm.data_received.connect(self.parse_response)

    def load_gcode_file(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            commands = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith(';'):
                    commands.append({
                        'line_number': i + 1,
                        'original': line,
                        'command': self.parse_gcode_line(line)
                    })

            return commands
        except Exception as e:
            print(f"Error loading G-code file: {e}")
            return []

    def parse_gcode_line(self, line):
        line = line.split(';')[0].strip()

        parts = line.split()
        if not parts:
            return None

        command = {
            'type': parts[0],
            'parameters': {}
        }

        for part in parts[1:]:
            if len(part) >= 2:
                param = part[0]
                try:
                    value = float(part[1:])
                    command['parameters'][param] = value
                except ValueError:
                    command['parameters'][param] = part[1:]

        return command

    def start_print(self, gcode_commands):
        if self.is_printing:
            return False

        self.gcode_commands = gcode_commands
        self.total_lines = len(gcode_commands)
        self.current_line = 0
        self.is_printing = True
        self.is_paused = False

        self.print_thread = threading.Thread(target=self.print_loop, daemon=True)
        self.print_thread.start()

        self.print_status_changed.emit("printing")
        return True

    def print_loop(self):
        while self.is_printing and self.current_line < self.total_lines:
            if self.is_paused:
                time.sleep(0.1)
                continue

            command_data = self.gcode_commands[self.current_line]
            command = command_data['original']

            if self.serial_comm.send_command(command):
                response = self.serial_comm.send_command_with_response(command, timeout=10.0)
                if response and 'error' in response.lower():
                    print(f"Error executing command: {command}")
                    break

            self.current_line += 1
            progress = int((self.current_line / self.total_lines) * 100)
            self.print_progress.emit(progress)

            parsed_command = command_data['command']
            if parsed_command:
                self.update_position_from_command(parsed_command)

            time.sleep(0.01)

        self.is_printing = False
        self.print_status_changed.emit("finished" if self.current_line >= self.total_lines else "stopped")

    def pause_print(self):
        if self.is_printing:
            self.is_paused = True
            self.print_status_changed.emit("paused")

    def resume_print(self):
        if self.is_printing and self.is_paused:
            self.is_paused = False
            self.print_status_changed.emit("printing")

    def stop_print(self):
        self.is_printing = False
        self.is_paused = False
        if self.print_thread:
            self.print_thread.join(timeout=2.0)
        self.print_status_changed.emit("stopped")

    def move_to_position(self, x, y, z, feedrate=3000):
        command = f"G1 X{x:.2f} Y{y:.2f} Z{z:.2f} F{feedrate}"
        self.send_command(command)
        self.current_position[0] = x
        self.current_position[1] = y
        self.current_position[2] = z
        self.position_changed.emit(x, y, z)

    def move_relative(self, axis, distance, feedrate=3000):
        self.send_command("G91")
        command = f"G1 {axis}{distance:.2f} F{feedrate}"
        self.send_command(command)
        self.send_command("G90")

        axis_index = {'X': 0, 'Y': 1, 'Z': 2, 'E': 3}
        if axis in axis_index:
            self.current_position[axis_index[axis]] += distance
            if axis != 'E':
                self.position_changed.emit(
                    self.current_position[0],
                    self.current_position[1],
                    self.current_position[2]
                )

    def home_all(self):
        self.send_command("G28")
        self.current_position = [0.0, 0.0, 0.0, 0.0]
        self.position_changed.emit(0.0, 0.0, 0.0)

    def home_axis(self, axis):
        self.send_command(f"G28 {axis}")
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}
        if axis in axis_index:
            self.current_position[axis_index[axis]] = 0.0
            self.position_changed.emit(
                self.current_position[0],
                self.current_position[1],
                self.current_position[2]
            )

    def set_speeds(self, print_speed, travel_speed):
        self.send_command(f"M203 X{travel_speed} Y{travel_speed} Z{travel_speed}")
        self.send_command(f"G1 F{print_speed}")

    def set_acceleration(self, acceleration):
        self.send_command(f"M204 S{acceleration}")

    def set_temperature(self, heater, temperature):
        if heater == 'extruder':
            self.send_command(f"M104 S{temperature}")
        elif heater == 'bed':
            self.send_command(f"M140 S{temperature}")

    def get_temperature(self):
        self.send_command("M105")

    def request_status(self):
        if self.serial_comm.is_connected:
            self.send_command("M105")
            self.send_command("M114")

    def send_command(self, command):
        if self.serial_comm:
            return self.serial_comm.send_command(command)
        return False

    def _send_command(self, command):
        return self.send_command(command)

    def parse_response(self, response):
        response = response.strip()

        if response.startswith('ok'):
            return

        temp_match = re.search(r'T:(\d+\.?\d*)\s*/(\d+\.?\d*)', response)
        if temp_match:
            current_temp = float(temp_match.group(1))
            target_temp = float(temp_match.group(2))
            self.temperatures['extruder']['current'] = current_temp
            self.temperatures['extruder']['target'] = target_temp
            self.temperature_changed.emit('extruder', current_temp, target_temp)

        bed_match = re.search(r'B:(\d+\.?\d*)\s*/(\d+\.?\d*)', response)
        if bed_match:
            current_temp = float(bed_match.group(1))
            target_temp = float(bed_match.group(2))
            self.temperatures['bed']['current'] = current_temp
            self.temperatures['bed']['target'] = target_temp
            self.temperature_changed.emit('bed', current_temp, target_temp)

        pos_match = re.search(r'X:(-?\d+\.?\d*)\s*Y:(-?\d+\.?\d*)\s*Z:(-?\d+\.?\d*)', response)
        if pos_match and not self.is_printing:
            x = float(pos_match.group(1))
            y = float(pos_match.group(2))
            z = float(pos_match.group(3))
            self.current_position[0] = x
            self.current_position[1] = y
            self.current_position[2] = z
            self.position_changed.emit(x, y, z)

    def update_position_from_command(self, command):
        if command['type'] in ['G0', 'G1']:
            params = command['parameters']
            if 'X' in params:
                self.current_position[0] = params['X']
            if 'Y' in params:
                self.current_position[1] = params['Y']
            if 'Z' in params:
                self.current_position[2] = params['Z']
            if 'E' in params:
                self.current_position[3] = params['E']

            self.position_changed.emit(
                self.current_position[0],
                self.current_position[1],
                self.current_position[2]
            )
        elif command['type'] == 'G28':
            params = command['parameters']
            if not params:
                self.current_position = [0.0, 0.0, 0.0, 0.0]
            else:
                if 'X' in params:
                    self.current_position[0] = 0.0
                if 'Y' in params:
                    self.current_position[1] = 0.0
                if 'Z' in params:
                    self.current_position[2] = 0.0

            self.position_changed.emit(
                self.current_position[0],
                self.current_position[1],
                self.current_position[2]
            )

    def get_current_position(self):
        return self.current_position.copy()

    def get_print_progress(self):
        if self.total_lines > 0:
            return int((self.current_line / self.total_lines) * 100)
        return 0

    def is_print_active(self):
        return self.is_printing

    def is_print_paused(self):
        return self.is_paused