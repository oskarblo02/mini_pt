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
sampling_rate = 200 # Hz
smplrt_div = int(1000 / sampling_rate) - 1
bus.write_byte_data(ICM20600_ADDR, 0x19, smplrt_div)

# Define the filter parameters
cutoff_frequency = 5 # Hz
nyquist_frequency = 0.5 * sampling_rate
order = 2
cutoff = cutoff_frequency / nyquist_frequency
b, a = butter(order, cutoff, btype='low')

# Initialize the buffer with zeros
buffer_len = 10
x_filtered_buffer = np.zeros(buffer_len)
y_filtered_buffer = np.zeros(buffer_len)
z_filtered_buffer = np.zeros(buffer_len)

# Initialize the velocity and displacement variables
vx = 0
vy = 0
vz = 0
vt = 0
prev_vx = 0
prev_vy = 0
prev_vz = 0
x_displacement = 0
y_displacement = 0
z_displacement = 0
t1 = 0
t2 = 0
dt = 0 
g = 9.82  # m/s^2


# Rep counting variabels
rep_start = False
rep_apex = False
rep_time = 0
rep_time_start = 0
rep_time_end = 0
rep_count = 0

# Initialize the plot
plt.ion()
fig, ax = plt.subplots()

# Define the plot parameters
x_axis = np.linspace(0, buffer_len-1, buffer_len)
raw_accel_x_plot, = ax.plot(x_axis, np.zeros(buffer_len), 'r-', label='ax')
raw_accel_y_plot, = ax.plot(x_axis, np.zeros(buffer_len), 'y-', label='ay')
raw_accel_z_plot, = ax.plot(x_axis, np.zeros(buffer_len), 'g-', label='az')
filtered_accel_sum_plot, = ax.plot(x_axis, np.zeros(buffer_len), 'b-', label='Filtered data')

ax.set_ylim([-3, 3])
ax.set_xlabel('Samples')
ax.set_ylabel('Acceleration (m/s^2)')
ax.legend()

# Continuously update the plot
while True:
    t1 = time.time()
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
    gravity_y = np.sin(roll) * np.cos(pitch) 
    gravity_z = np.cos(pitch) * np.cos(roll) 
    
    
    # Convert the raw accelerometer data to acceleration in m/s^2 and subtract the gravity acceleration
    #accel_x = (int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0]) - gravity_x
    #accel_y = (int.from_bytes(accel_y_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0]) - #gravity_y
    #accel_z = (int.from_bytes(accel_z_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0]) - #gravity_z
    
    # Append the latest x-axis acceleration to the buffer and filter it
    x_filtered_buffer = np.append(x_filtered_buffer, accel_x)
    x_filtered_buffer = x_filtered_buffer[-buffer_len:]
    x_filtered = filtfilt(b, a, x_filtered_buffer)

    
    # Append the latest y-axis acceleration to the buffer and filter it
    y_filtered_buffer = np.append(y_filtered_buffer, accel_y)
    y_filtered_buffer = y_filtered_buffer[-buffer_len:]
    y_filtered = filtfilt(b, a, y_filtered_buffer)

    # Append the latest z-axis acceleration to the buffer and filter it
    z_filtered_buffer = np.append(z_filtered_buffer, accel_z)
    z_filtered_buffer = z_filtered_buffer[-buffer_len:]
    z_filtered = filtfilt(b, a, z_filtered_buffer)
    
    accel_sum = np.sqrt(x_filtered_buffer**2 + y_filtered_buffer**2 + z_filtered_buffer**2) - 1
    accel_sum *= g
    accel_sum_filt = np.sqrt(x_filtered**2 + y_filtered**2 + z_filtered**2) - 1
    accel_sum_filt *= g
    t2 = time.time()
    dt = t2-t1
    #calculate velocity 
    vx += (x_filtered[-1] + x_filtered[-2]) / 2 / sampling_rate
    vy += (y_filtered[-1] + y_filtered[-2]) / 2 / sampling_rate
    vz += (z_filtered[-1] + z_filtered[-2]) / 2 / sampling_rate
    
    vt = np.sqrt(vx**2 + vy**2 + vx**2)
    
    x_displacement += (vx + prev_vx) / 2 / sampling_rate
    y_displacement += (vy + prev_vy) / 2 / sampling_rate
    z_displacement += (vz + prev_vz) / 2 / sampling_rate

    
    print("Velocity in X direction: ", np.round(vx, 2), "m/s")
    print("Velocity in Y direction: ", np.round(vy, 2), "m/s")
    print("Velocity in Z direction: ", np.round(vz, 2), "m/s")
    print("Velocity in T direction: ", np.round(vt, 2), "m/s")
    
    # Print the acceleration in m/s^2
    #print("Acceleration in X direction: ", np.round(x_filtered, 2), "m/s^2")
    #print("Acceleration in Y direction: ", np.round(y_filtered, 2), "m/s^2")
    #print("Acceleration in Z direction: ", np.round(z_filtered, 2), "m/s^2")
    print("Acceleration: ", np.round(accel_sum_filt, 2), "m/s^2")
    
    # Update the plot
    raw_accel_x_plot.set_ydata(z_filtered)
    raw_accel_y_plot.set_ydata(y_filtered)
    raw_accel_z_plot.set_ydata(z_filtered)
    filtered_accel_sum_plot.set_ydata(accel_sum_filt)
    plt.pause(0.001)
    time.sleep(1/sampling_rate)

