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

# Initialize variables
reps = 0
accel_sum_prev = 0
accel_sum_mid = 0
accel_sum_zero = 0
rep_start = False
rep_top = False
rep_end = False
time_start = 0
time_end = 0
time_elapsed = [0 for i in range(100)]

while True:
    # Read the raw accelerometer data from the sensor
    accel_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_XOUT_H, 2)
    accel_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_YOUT_H, 2)
    accel_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_ZOUT_H, 2)

    # Convert the raw accelerometer data to acceleration in m/s^2
    accel_x = int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81
    accel_y = int.from_bytes(accel_y_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81
    accel_z = int.from_bytes(accel_z_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81

    # Calculates the sum of all vectors
    accel_sum = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

    for i in range(100000): 
        accel_sum_mid += accel_sum
        
    accel_sum_mid /= 100000
    accel_sum_zero = accel_sum_mid - 9.9
        
    if accel_sum_zero > 2 and not rep_start:
        rep_start = True
        time_elapsed[reps+1] = 0
        time_start = time.time()
    
    if (accel_sum_zero < 1) and (accel_sum_zero > -1)  and rep_start:
        #if not rep_top:
            #reps += 1
            #print("Rep completed, total count:", reps)
        rep_top = True
    time.sleep(0.3)
    if (accel_sum_zero < 1) and (accel_sum_zero > -1)  and rep_top:
        if not rep_end:
            reps += 1
            print("Rep completed, total count:", reps)
        rep_end = True
        rep_top = False
        time_end = time.time()
        time_elapsed[reps] = time_end - time_start
    else:
        rep_end = False
     
    for i in range(reps):
        print("rep", i+1, "time", round(time_elapsed[i+1], 2), "s")
    
    accel_sum_prev = accel_sum_mid
    
    # Print the acceleration in m/s^2
    #print("Acceleration in X direction: ", round(accel_x, 2), "m/s^2")
    #print("Acceleration in Y direction: ", round(accel_y, 2), "m/s^2")
    #print("Acceleration in Z direction: ", round(accel_z, 2), "m/s^2")
    #print("Acceleration: ", round(accel_sum, 2), "m/s^2")
    print("Acceleration Mid: ", round(accel_sum_mid, 2), "m/s^2")
    print("Acceleration Zero: ", round(accel_sum_zero, 2), "m/s^2")
    print("Reps: ", reps, "st")
    #print("Rep time:", round(time_elapsed, 2) , "s")
    time.sleep(0.1)
