import serial
import serial.tools.list_ports
import threading
import time
import queue
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread

class SerialComm(QObject):
    data_received = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_reading = False
        self.response_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.write_thread = None
        
        self.baudrate = 115200
        self.timeout = 1.0
        self.write_timeout = 1.0
        
        self.start_write_thread()
    
    def list_available_ports(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports
    
    def connect(self, port, baudrate=115200):
        try:
            if self.is_connected:
                self.disconnect()
            
            self.baudrate = baudrate
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            self.is_connected = True
            self.stop_reading = False
            self.start_read_thread()
            
            self.connection_changed.emit(True)
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            self.connection_changed.emit(False)
            return False
    
    def disconnect(self):
        self.is_connected = False
        self.stop_reading = True
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.serial_port = None
        self.connection_changed.emit(False)
    
    def start_read_thread(self):
        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.read_thread.start()
    
    def start_write_thread(self):
        self.write_thread = threading.Thread(target=self.write_loop, daemon=True)
        self.write_thread.start()
    
    def read_loop(self):
        while not self.stop_reading and self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if data:
                        self.response_queue.put(data)
                        self.data_received.emit(data)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"Read error: {e}")
                break
    
    def write_loop(self):
        while True:
            try:
                command = self.command_queue.get(timeout=1.0)
                if command is None:
                    break
                
                if self.is_connected and self.serial_port:
                    self.serial_port.write((command + '\n').encode('utf-8'))
                    self.serial_port.flush()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Write error: {e}")
    
    def send_command(self, command):
        if self.is_connected:
            self.command_queue.put(command)
            return True
        return False
    
    def send_command_with_response(self, command, timeout=5.0):
        if not self.send_command(command):
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.response_queue.get(timeout=0.1)
                if 'ok' in response.lower() or 'error' in response.lower():
                    return response
            except queue.Empty:
                continue
        
        return None
    
    def get_all_responses(self):
        responses = []
        while not self.response_queue.empty():
            try:
                responses.append(self.response_queue.get_nowait())
            except queue.Empty:
                break
        return responses
    
    def clear_response_queue(self):
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break
    
    def is_port_available(self, port):
        try:
            test_serial = serial.Serial(port, timeout=0.1)
            test_serial.close()
            return True
        except:
            return False
    
    def get_connection_info(self):
        if self.is_connected and self.serial_port:
            return {
                'port': self.serial_port.port,
                'baudrate': self.serial_port.baudrate,
                'timeout': self.serial_port.timeout,
                'is_open': self.serial_port.is_open
            }
        return None
    
    def __del__(self):
        self.disconnect()
        if self.write_thread:
            self.command_queue.put(None)

