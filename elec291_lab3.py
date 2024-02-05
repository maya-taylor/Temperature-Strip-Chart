import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import serial
import tkinter as tk
import tkinter.messagebox as tkmb
from tkinter import ttk, simpledialog

# Global variables
maxTemp = None
xdata, ydata_celsius, ydata_derivative = [], [], []

def get_max_temperature():
    global maxTemp
    maxTemp = simpledialog.askfloat("Input", "Enter the max safe temperature:")
    if maxTemp is not None:
        print(f"Ideal max temperature set to: {maxTemp}°C")
        # Start temperature monitoring and graphing after getting the ideal max temperature
        start_monitoring()

#def is_safe_temperature(val):
    #return 24.0 <= val <= 25.0

# configure the serial port
ser = serial.Serial(
    port='COM10',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)

xsize = 100

def data_gen():
    data_gen.t = -1
    info_win = 0
    previous_val = 0  # Initialize previous value
    while True:
        data_gen.t += 1
        strin = ser.readline()
        temp_val = strin[2:7]
        val = float(temp_val)
        print(temp_val)

        # Convert temperature to Fahrenheit if needed
        derivative_val = 0 if data_gen.t == 0 else (val - previous_val) / 1  # Assuming constant time interval of 1

        if val > maxTemp and info_win == 0:
            tkmb.showinfo("Temperature Alert", "Temperature is in an unsafe range!")
            info_win = 1
        if val < maxTemp-1.0 and info_win == 1:
            tkmb.showinfo("Temperature Alert", "Temperature has returned to a safe range")
            info_win = 0

        previous_val = val
        yield data_gen.t, val, derivative_val

def run(data):
    t, y_celsius, y_derivative = data
    if t > -1:
        xdata.append(t)
        ydata_celsius.append(y_celsius)
        ydata_derivative.append(y_derivative)
        if t > xsize:
           ax.set_xlim(t - xsize, t)
        line_celsius.set_data(xdata, ydata_celsius)
        line_derivative.set_data(xdata, ydata_derivative)
    return line_celsius, line_derivative

def on_close_figure(event):
    ser.close()
    sys.exit(0)

def start_monitoring():
    def run(data):
        t, y_celsius, y_derivative = data
        if t > -1:
            xdata.append(t)
            ydata_celsius.append(y_celsius)
            ydata_derivative.append(y_derivative)
            if t > xsize:
                ax.set_xlim(t - xsize, t)
            line_celsius.set_data(xdata, ydata_celsius)
            line_derivative.set_data(xdata, ydata_derivative)
        return line_celsius, line_derivative

    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('close_event', on_close_figure)

    global line_celsius, line_derivative
    line_celsius, = ax.plot([], [], lw=2, color='pink', label='Celsius')
    line_derivative, = ax.plot([], [], lw=2, color='blue', label='Derivative of Celsius')

    ax.set_ylim(-5, 70)
    ax.set_xlim(0, xsize)

    ax.grid()

    ax.set_title("Temperature and Derivative of LM355 Sensor", fontsize=15)
    ax.set_ylabel("Temperature and Derivative", color='black')
    plt.xlabel("Time (s)", color='black')
    plt.legend()

    ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=100, repeat=False)
    plt.show()

# Create the main window
root = tk.Tk()
root.title("Temperature Monitoring System")

# Button to set the ideal max temperature
button = tk.Button(root, text="Set Ideal Max Temperature", command=get_max_temperature)
button.pack(pady=20)

# Start the main loop
root.mainloop()
