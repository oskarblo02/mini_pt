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
rep_start = False
rep_top = False
rep_end = False

accel_sum_mid = 0
accel_sum_zero = 0
accel_sum_zero_last = 0


speed = 0
speed_avg = 0
speed_time = 0
speed_reset = 0

t1 = 0
t2 = 0
dt = 0


time_start = 0
time_start_og = 0
time_end = 0
total_time = []
time_elapsed = []

elements = 0

gravity = 0
grav_yes = False

speed_list = []
list_accel_sum = []
list_accel_zero = []

def acceleration():
    # Read the raw accelerometer data from the sensor
    accel_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_XOUT_H, 2)
    accel_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_YOUT_H, 2)
    accel_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_ZOUT_H, 2)

    # Convert the raw accelerometer data to acceleration in m/s^2
    accel_x = int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81
    accel_y = int.from_bytes(accel_y_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81
    accel_z = int.from_bytes(accel_z_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81

    # Calculates the sum of all vectors
    accel_sum  = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    return accel_sum
    
speed = 0
t2 = time.monotonic()
accel_sum_zero_last = 0
dt = 0

while True:
    
        # calibrates the gravity
    if grav_yes == False:
        for i in range(1000): 
            accel_sum_mid += acceleration()
        accel_sum_mid /= 1000
        gravity = accel_sum_mid
        grav_yes = True
        print("GO GO GO!!!")
    # calculate acceleration
    accel_sum_zero = acceleration() - gravity
    
    # if the acceleration is below the threshold, assume stationary and set speed to zero
    if abs(accel_sum_zero) > 0.1:
        # calculate velocity using trapezoidal rule
        t1 = time.monotonic()
        dt = t1 - t2
    if accel_sum_zero < 0:
        speed -= ((-1*accel_sum_zero + accel_sum_zero_last) / 2) * dt
    else:
        speed += ((accel_sum_zero + accel_sum_zero_last) / 2) * dt
        t2 = t1
        accel_sum_zero_last = accel_sum_zero
    else:
        speed = 0
    
    print("Acceleration:", round(accel_sum_zero, 2), "m/s^2, Speed: ", round(speed, 2), "m/s, dt:", dt)
    
    # adds the newest value to the last place in the lists
    speed_list.append(speed)
    list_accel_sum.append(acceleration())
    list_accel_zero.append(accel_sum_zero)

    elements += 1
    
    total_time.append(time.monotonic()- time_start_og)
    time_elapsed.append(time.monotonic() - time_start)
    

    # Writes to temp file for easy analysis 
    #if KeyboardInterrupt == True:
    #    print("hej")
    with open("temp.csv", "w") as f:
        f.write("time;accel;accel_zero;speed;total time;\n")
        for i in range(elements):
            f.write(f"{time_elapsed[i]};{list_accel_sum[i]};{list_accel_zero[i]};{speed_list[i]};{total_time[i]};\n")
