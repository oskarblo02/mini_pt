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

# Register addresses for the gyroscope data
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# Accelerometer sensitivity in LSB/g
AFS_SEL_SENSITIVITY = {
    0: 16384,
    1: 8192,
    2: 4096,
    3: 2048
}

# Gyroscope sensitivity in LSB/(deg/s)
GFS_SEL_SENSITIVITY = {
    0: 131,
    1: 65.5,
    2: 32.8,
    3: 16.4
}

# Initialize I2C bus and open a connection to the ICM20600 sensor
bus = smbus2.SMBus(7)
bus.write_byte_data(ICM20600_ADDR, 0x6B, 0x00)

#bra att ha variabler
reps = 0
accel_sum_mid = 0
accel_sum_zero = 0
rep_start = 0
gravity = 0
grav_yes = False

# Initialize variables for velocity calculation
gyro_x_sum = 0
gyro_y_sum = 0
gyro_z_sum = 0
last_time = time.time()
# Initialize variables for velocity calculation
prev_gyro = 0
prev_accel = 0
velocity = 0

t1 = 0
t2 = 0
dt = 0

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

#def gyro():
        # Read the raw gyroscope data from the sensor
    gyro_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, GYRO_XOUT_H, 2)
    gyro_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, GYRO_YOUT_H, 2)
    gyro_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, GYRO_ZOUT_H, 2)

    # Convert the raw gyroscope data to angular velocity in degrees/s
    gyro_x = int.from_bytes(gyro_x_raw, byteorder='big', signed=True) / GFS_SEL_SENSITIVITY[0]
    gyro_y = int.from_bytes(gyro_y_raw, byteorder='big', signed=True) / GFS_SEL_SENSITIVITY[0]
    gyro_z = int.from_bytes(gyro_z_raw, byteorder='big', signed=True) / GFS_SEL_SENSITIVITY[0]
    
    # Calculates the sum of all vectors
    gyro_sum  = math.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)
    print("gyro x", gyro_x)
    print("gyro y", gyro_y)
    print("gyro z", gyro_z)
    print("gyro s", gyro_sum)
    return gyro_sum


t2 = time.monotonic()

while True:

            # calibrates the gravity
    if grav_yes == False:
        for i in range(1000): 
            accel_sum_mid += acceleration()
        accel_sum_mid /= 1000
        gravity = accel_sum_mid
        grav_yes = True
        print("GO GO GO!!!")
    
    accel_sum_zero = acceleration() - gravity
    
    # Calculate the change in acceleration and angular velocity
    delta_accel = accel_sum_zero - prev_accel
    #delta_gyro = gyro() - prev_gyro

    # Update the previous acceleration and angular velocity values
    prev_accel = accel_sum_zero
    #prev_gyro = gyro()
    
    t1 = time.monotonic()
    dt = t1 - t2
    t2 = t1
    # Calculate the velocity using the trapezoidal rule
    #velocity += ((delta_accel + delta_gyro) / 2) * dt

    # Print the acceleration and velocity in m/s^2 and m/s
    print("Acceleration: ", round(prev_accel, 2), "m/s^2")
    #print("Velocity: ", round(velocity, 2), "m/s")

    # Wait for the next time step
    #time.sleep(dt)
