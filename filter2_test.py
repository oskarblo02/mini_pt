import smbus2
import time
import math

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
sampling_rate = 20

# Calculate the new value for the SMPLRT_DIV register
smplrt_div_value = int(1000 / sampling_rate) - 1




# Number of samples to use in the moving average filter
N_SAMPLES = 6

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
rep_start = False
rep_apex = False
rep_end = True
rep_time = [0 for i in range(1000)]
rep_time_start = 0
rep_time_end = 0
apex_time = 0
rep_count = 0
rep_disp = [0 for i in range(1000)]
peak_accel = 0
rep_avg_speed = [0 for i in range(1000)]
num_samples = 0
time_interval = 0

while True:
    # Read the raw accelerometer data from the sensor
    accel_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_XOUT_H, 2)
    accel_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_YOUT_H, 2)
    accel_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_ZOUT_H, 2)

    # Convert the raw accelerometer data to acceleration in m/s^2
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

    if accel_sum_filt > 1.05 and rep_end:
        rep_start = True
        print("START")
        rep_time_start = time.time()
        rep_end = False
        rep_stay = False
        
    if rep_start and not rep_apex:
        if accel_sum_filt > 1.02 or accel_sum_filt < 0.98:
            accel_sampels.append((accel_sum_filt * 9.82) - 9.82)
        
    if accel_sum_filt < 0.95 and rep_start and not rep_apex:
        rep_apex = True
        apex_time = time.time() - rep_time_start
        print("APEX")
        num_samples = len(accel_sampels) 
        time_interval = apex_time / num_samples

        
    if accel_sum_filt > 1.05 and rep_start and rep_apex:
        rep_count += 1
        rep_start = False
        rep_apex = False
        rep_end = True
        
        print("END")
        rep_time_end = time.time()
        rep_time[rep_count-1] = rep_time_end - rep_time_start
        for i in range(1, num_samples):
            rep_avg_speed[rep_count-1] = rep_avg_speed[rep_count-1] + 0.5 * (accel_sampels[i] + accel_sampels[i-1]) * time_interval 
        accel_sampels.pop()
        rep_disp[rep_count-1] = apex_time * rep_avg_speed[rep_count-1]
        
    # Print results
    #print("Rep count:", rep_count)
    #print("Rep time:", round(rep_time[rep_count-1], 2), "s")
    #print("Rep displacement:", round(rep_disp, 2), "m")
    #print("Rep average speed:", round(rep_avg_speed, 2), "m/s")
    
    # Print the acceleration in m/s^2
    #print("Acceleration in X direction: ", round(accel_x, 2), "g")
    #print("Acceleration in Y direction: ", round(accel_y, 2), "g")
    #print("Acceleration in Z direction: ", round(accel_z, 2), "g")
    #print("Acceleration: ", round(accel_sum, 2), "g")
    print("Filtered acceleration: ", round(accel_sum_filt, 2), "g")
    #print("reps: ", rep_count, "st, last rep time:", rep_time[rep_count], "s")
    #for i in range(rep_count):
    #    print("Reps:", i+1, "st, Time:", round(rep_time[i], 2), "s, ROM:", round(rep_disp[i], 2), "m, Speed:", round(rep_avg_speed[i], 2), "m/s")

    time.sleep(1/sampling_rate)
