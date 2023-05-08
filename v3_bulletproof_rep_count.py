import smbus2
import time
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
from tinydb import TinyDB, Query

# Create a database object and specify the file name
db = TinyDB('minipt.json')

setcount = 1

# Create a table object and specify the table name
table_name = 'set' + str(setcount)
table = db.table(table_name)

# I2C address of the ICM20600 sensor
ICM20600_ADDR = 0x69

# Register addresses for the accelerometer data
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40

# Register address for the accelerometer configuration
ACCEL_CONFIG2 = 0x1D

# Accelerometer sensitivity in LSB/g
AFS_SEL_SENSITIVITY = {
    0: 16384,
    1: 8192,
    2: 4096,
    3: 2048
}

# Register address for the Sample Rate Divider
SMPLRT_DIV = 0x19

# Set the desired sampling rate (e.g. 100 Hz)
sampling_rate = 200

# Calculate the new value for the SMPLRT_DIV register
smplrt_div_value = int(1000 / sampling_rate) - 1

# Number of samples to use in the moving average filter
N_SAMPLES = 10

# Initialize I2C bus and open a connection to the ICM20600 sensor
bus = smbus2.SMBus(7)
bus.write_byte_data(ICM20600_ADDR, ACCEL_CONFIG2, 0x09)
bus.write_byte_data(ICM20600_ADDR, 0x6B, 0x00)
# Write the new value to the SMPLRT_DIV register
bus.write_byte_data(ICM20600_ADDR, SMPLRT_DIV, smplrt_div_value)

# Initialize a buffer for the accelerometer data
accel_buffer = []
accel_sampels = []

# Rep counting variabels
rep_count = 0
rep_time = np.zeros(100)
up_time = np.zeros(100)
down_time = np.zeros(100)
extreme_explosive_power_factor = np.zeros(100)
time_start = 0
moving_up = False
moving_down = False
up = False
down = False
been_down = False
been_up = False
stationary = True
start_point = True
check_up = False
check_down = False
check_time = False
high = 0
low = 0

ACCEL_UP = 1.05
ACCEL_DOWN = 0.95



while True:
    # Read the raw accelerometer data from the sensor
    accel_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_XOUT_H, 2)
    accel_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_YOUT_H, 2)
    accel_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_ZOUT_H, 2)

    # Convert the raw accelerometer data to acceleration in g
    accel_x = int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] 
    accel_y = int.from_bytes(accel_y_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] 
    accel_z = int.from_bytes(accel_z_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] 

    # Calculates the sum of all vectors
    accel_sum = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

    # Add the current accelerometer reading to the buffer
    accel_buffer.append(accel_sum)

    # If the buffer is full, remove the oldest reading
    if len(accel_buffer) > N_SAMPLES:
        accel_buffer.pop(0)

    # Calculate the moving average of the accelerometer data
    accel_sum_filt = sum(accel_buffer) / len(accel_buffer)

    # Checks if the movment is up
    if accel_sum_filt > ACCEL_UP and high == 0 and not moving_down:
        moving_up = True
        start_point = False
        stationary = False
        time_start = time.time()
        high  = 1
    if accel_sum_filt < ACCEL_UP and high == 1 and not moving_down:
        high  = 2
    if accel_sum_filt < ACCEL_DOWN and high == 2 and not moving_down:
        high  = 3
    if accel_sum_filt > ACCEL_DOWN and high == 3 and not moving_down:
        stationary = True
        up = True
        been_up = True
        moving_up = False
        high = 0
        if not check_up:
            up_time[rep_count] = time.time() - time_start
            check_up = True

    # Checks if the movment is down
    if accel_sum_filt < ACCEL_DOWN and low == 0 and not moving_up:
        moving_down = True
        start_point = False
        stationary = False
        time_start = time.time()
        low  = 1
    if accel_sum_filt > ACCEL_DOWN and low == 1 and not moving_up:
        low  = 2
    if accel_sum_filt > ACCEL_UP and low == 2 and not moving_up:
        low  = 3
    if accel_sum_filt < ACCEL_UP and low == 3 and not moving_up:
        stationary = True
        down = True
        been_down = True
        moving_down = False
        low = 0
        if not check_down:
            down_time[rep_count] = time.time() - time_start
            check_down = True
        

    if been_down and been_up:
        rep_time[rep_count] = down_time[rep_count] + up_time[rep_count]
        # Calculates a explosive power score based on the duration of the eccentric part of the rep  
        if up_time[rep_count] < 0.25:
            extreme_explosive_power_factor[rep_count] = 100
        elif up_time[rep_count] > 10.25:
            extreme_explosive_power_factor[rep_count] = 0
        else:
            extreme_explosive_power_factor[rep_count] = (10.25 - up_time[rep_count]) * 10
        # Resets all checks to start reading the next rep
        been_up = False
        been_down = False
        check_down = False
        check_up = False
        check_time = False
        start_point = True
        rep_count +=1
        # Add the rep count to the database
        table.insert({'rep_count': rep_count, 'rep_time': round(rep_time[rep_count-1], 2), 'EEPF': round(extreme_explosive_power_factor[rep_count-1], 2)})
       
       
    print("accel        ", round(accel_sum_filt, 2))

    for i in range(rep_count):
        print("reps:        ", i+1)
        print("up time      ", round(up_time[i], 2))
        print("down time    ", round(down_time[i], 2))
        print("rep time:    ", round(rep_time[i], 2))
        print("EEPF         ", round(extreme_explosive_power_factor[i]*100, 2), "%")
        
    

    
    time.sleep(1/sampling_rate)
        
        

