import sys
import serial
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sqlite3

# Gyroscope sensitivity (conversion factor for ±250°/s)
GYRO_SCALE = 131  # LSB value that corresponds to 1°/s for ±250°/s

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Acceleration and Gyroscope Data Analysis")
        self.setGeometry(100, 100, 1000, 700)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        # Layout for the entire content (graphs and table)
        overall_layout = QVBoxLayout()
        layout.addLayout(overall_layout)

        # Create X, Y, Z graphs for Acceleration
        graph_layout = QHBoxLayout()
        overall_layout.addLayout(graph_layout)

        # Create separate layout for each graph (X, Y, Z)
        self.figure_acc_x = plt.figure(figsize=(8, 6))
        self.canvas_acc_x = FigureCanvas(self.figure_acc_x)
        ax_acc_x = self.figure_acc_x.add_subplot(111)
        ax_acc_x.set_title("X Acceleration")
        ax_acc_x.set_xlabel("Time (s)")
        ax_acc_x.set_ylabel("Acceleration (m/s²)")
        graph_layout.addWidget(self.canvas_acc_x)

        self.figure_acc_y = plt.figure(figsize=(8, 6))
        self.canvas_acc_y = FigureCanvas(self.figure_acc_y)
        ax_acc_y = self.figure_acc_y.add_subplot(111)
        ax_acc_y.set_title("Y Acceleration")
        ax_acc_y.set_xlabel("Time (s)")
        ax_acc_y.set_ylabel("Acceleration (m/s²)")
        graph_layout.addWidget(self.canvas_acc_y)

        self.figure_acc_z = plt.figure(figsize=(8, 6))
        self.canvas_acc_z = FigureCanvas(self.figure_acc_z)
        ax_acc_z = self.figure_acc_z.add_subplot(111)
        ax_acc_z.set_title("Z Acceleration")
        ax_acc_z.set_xlabel("Time (s)")
        ax_acc_z.set_ylabel("Acceleration (m/s²)")
        graph_layout.addWidget(self.canvas_acc_z)

        # Data table for Acceleration and Gyroscope data
        self.table = QTableWidget(self)
        self.table.setRowCount(0)  # Initially empty
        self.table.setColumnCount(8)  # Measurement ID, Acceleration X, Y, Z, Gyroscope X, Y, Z, Date
        self.table.setHorizontalHeaderLabels(
            ["Measurement ID", "X Acceleration (m/s²)", "Y Acceleration (m/s²)", "Z Acceleration (m/s²)",
             "X Gyroscope (°/s)", "Y Gyroscope (°/s)", "Z Gyroscope (°/s)", "Date"]
        )
        overall_layout.addWidget(self.table)

        # SQLite database initialization
        self.connection = sqlite3.connect("sensor_data.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER,
                x_acc REAL,
                y_acc REAL,
                z_acc REAL,
                x_gyro REAL,
                y_gyro REAL,
                z_gyro REAL,
                time TEXT
            )
        """)
        self.connection.commit()

        # Serial port initialization with error handling
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)  # Adjust COM port as needed
        except serial.SerialException:
            self.serial_port = None
            QMessageBox.warning(self, "Serial Port Error", "Arduino is not connected. Please check the connection.")

        # Data storage
        self.acceleration_data = {'x': [], 'y': [], 'z': []}
        self.gyroscope_data = {'x': [], 'y': [], 'z': []}
        self.time = []
        self.measurement_id = 0

        # Timer for reading serial data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(1000)  # Check for data every 1000 ms (1 second)

    def update_graph(self):
        """ Update the acceleration graph with the latest data """
        if len(self.acceleration_data['x']) == 0:
            return  # No data to plot

        # Clear and plot new acceleration data in X, Y, Z axes
        self.figure_acc_x.clear()  # Clear previous plot
        ax_acc_x = self.figure_acc_x.add_subplot(111)
        ax_acc_x.plot(self.time, self.acceleration_data['x'], label="X Acceleration", color='r')
        ax_acc_x.set_title("X Acceleration")
        ax_acc_x.set_xlabel("Time (s)")
        ax_acc_x.set_ylabel("Acceleration (m/s²)")

        self.figure_acc_y.clear()
        ax_acc_y = self.figure_acc_y.add_subplot(111)
        ax_acc_y.plot(self.time, self.acceleration_data['y'], label="Y Acceleration", color='g')
        ax_acc_y.set_title("Y Acceleration")
        ax_acc_y.set_xlabel("Time (s)")
        ax_acc_y.set_ylabel("Acceleration (m/s²)")

        self.figure_acc_z.clear()
        ax_acc_z = self.figure_acc_z.add_subplot(111)
        ax_acc_z.plot(self.time, self.acceleration_data['z'], label="Z Acceleration", color='b')
        ax_acc_z.set_title("Z Acceleration")
        ax_acc_z.set_xlabel("Time (s)")
        ax_acc_z.set_ylabel("Acceleration (m/s²)")

        self.canvas_acc_x.draw()
        self.canvas_acc_y.draw()
        self.canvas_acc_z.draw()

    def read_serial_data(self):
        if not self.serial_port:
            return  # If the serial port is not connected, do nothing

        if self.serial_port.in_waiting > 0:
            line = self.serial_port.readline().decode('utf-8').strip()
            try:
                # Parse the data (format: X,Y,Z,GX,GY,GZ)
                x, y, z, gx_raw, gy_raw, gz_raw = map(float, line.split(','))
                self.measurement_id += 1

                # Convert gyroscope raw values to degrees per second
                gx = gx_raw / GYRO_SCALE
                gy = gy_raw / GYRO_SCALE
                gz = gz_raw / GYRO_SCALE

                # Get current timestamp
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Update acceleration and gyroscope data
                self.acceleration_data['x'].append(x)
                self.acceleration_data['y'].append(y)
                self.acceleration_data['z'].append(z)
                self.gyroscope_data['x'].append(gx)
                self.gyroscope_data['y'].append(gy)
                self.gyroscope_data['z'].append(gz)

                self.time.append(current_time)

                # Update table (Acceleration and Gyroscope data)
                self.table.insertRow(self.measurement_id - 1)
                self.table.setItem(self.measurement_id - 1, 0, QTableWidgetItem(str(self.measurement_id)))
                self.table.setItem(self.measurement_id - 1, 1, QTableWidgetItem(f"{x:.2f}"))
                self.table.setItem(self.measurement_id - 1, 2, QTableWidgetItem(f"{y:.2f}"))
                self.table.setItem(self.measurement_id - 1, 3, QTableWidgetItem(f"{z:.2f}"))
                self.table.setItem(self.measurement_id - 1, 4, QTableWidgetItem(f"{gx:.2f}"))
                self.table.setItem(self.measurement_id - 1, 5, QTableWidgetItem(f"{gy:.2f}"))
                self.table.setItem(self.measurement_id - 1, 6, QTableWidgetItem(f"{gz:.2f}"))
                self.table.setItem(self.measurement_id - 1, 7, QTableWidgetItem(current_time))

                # Save to SQLite database
                self.cursor.execute(""" 
                    INSERT INTO data (measurement_id, x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, time) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                    (self.measurement_id, x, y, z, gx, gy, gz, current_time))
                self.connection.commit()

                # Update the graph with the new acceleration data
                self.update_graph()

            except ValueError:
                print("Invalid data received. Skipping...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
