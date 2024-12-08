import serial.tools.list_ports


class SerialPortReader:
    def __init__(self):
        self.ports = serial.tools.list_ports.comports()
        self.serial_instance = serial.Serial()
        self.serial_instance.baudrate = 9600
        self.port = None

    def show_ports(self):
        for port in self.ports:
            print(port)

    def connect(self, value: str):
        for port in self.ports:
            if port.device.startswith("COM" + value):
                self.port = port.device
                print(f"Connecting to {self.port}")
                self.serial_instance.port = self.port
                self.serial_instance.open()
                return
        print(f"No matching port found for COM{value}")

    def get_data(self):
        if self.serial_instance.in_waiting:
            packet = self.serial_instance.readline()
            return packet
        return None

    def send_data(self, data):
        self.serial_instance.write(data.encode('utf-8'))

    def close(self):
        if self.serial_instance.is_open:
            self.serial_instance.close()
            print(f"Closed connection to {self.port}")
