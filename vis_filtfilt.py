import smbus2
import time
import math
import numpy as np
from scipy.signal import filtfilt, butter
import matplotlib.pyplot as plt

# I2C address of the ICM20600 sensor
ICM20600_ADDR = 0x69

# Register addresses for the accelerometer data
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40

# Accelerometer sensitivity in LSB/g
AFS_SEL_SENSITIVITY = {
    0: 16384,
    1: 8192,
    2: 4096,
    3: 2048
}

# Initialize I2C bus and open a connection to the ICM20600 sensor
bus = smbus2.SMBus(7)
bus.write_byte_data(ICM20600_ADDR, 0x6B, 0x00)

# Set the sample rate divider to 4 for a desired sampling rate of 200 Hz
sampling_rate = 100 # Hz
smplrt_div = int(1000 / sampling_rate) - 1
bus.write_byte_data(ICM20600_ADDR, 0x19, smplrt_div)

# Define the filter parameters
cutoff_frequency = 20 # Hz
nyquist_frequency = 0.5 * sampling_rate
order = 2
cutoff = cutoff_frequency / nyquist_frequency
b, a = butter(order, cutoff, btype='low')

# Initialize the buffer with zeros
buffer_len = 10
x_filtered_buffer = np.zeros(buffer_len)
y_filtered_buffer = np.zeros(buffer_len)
z_filtered_buffer = np.zeros(buffer_len)

# Initialize the velocity variables
vx = 0
vy = 0
vz = 0

g = 9.82  # m/s^2


# Initialize the plot
plt.ion()
fig, ax = plt.subplots()

# Define the plot parameters
x_axis = np.linspace(0, buffer_len-1, buffer_len)
raw_accel_x_plot, = ax.plot(x_axis, np.zeros(buffer_len), 'r-', label='Raw data')
filtered_accel_x_plot, = ax.plot(x_axis, np.zeros(buffer_len), 'b-', label='Filtered data')
ax.set_ylim([-10, 10])
ax.set_xlabel('Samples')
ax.set_ylabel('Acceleration (m/s^2)')
ax.legend()

# Continuously update the plot
while True:
    # Read the raw accelerometer data from the sensor
    accel_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_XOUT_H, 2)
    accel_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_YOUT_H, 2)
    accel_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_ZOUT_H, 2)

    # Convert the raw accelerometer data to acceleration in m/s^2 and subtract the gravity acceleration
    accel_x = (int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0])
    accel_y = (int.from_bytes(accel_y_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0])
    accel_z = (int.from_bytes(accel_z_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0])
    
    roll = math.atan2(accel_y, accel_z)
    pitch = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2))
        
    gravity_x = np.sin(pitch) * np.cos(roll) 

    
    # Convert the raw accelerometer data to acceleration in m/s^2 and subtract the gravity acceleration
    accel_x = (int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0]) - gravity_x
    
    # Append the latest x-axis acceleration to the buffer and filter it
    x_filtered_buffer = np.append(x_filtered_buffer, accel_x)
    x_filtered_buffer = x_filtered_buffer[-buffer_len:]
    x_filtered = filtfilt(b, a, x_filtered_buffer)

    # Update the plot
    raw_accel_x_plot.set_ydata(x_filtered_buffer)
    filtered_accel_x_plot.set_ydata(x_filtered)
    plt.pause(0.001)
