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

while True:
    # Read the raw accelerometer data from the sensor
    accel_x_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_XOUT_H, 2)
    accel_y_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_YOUT_H, 2)
    accel_z_raw = bus.read_i2c_block_data(ICM20600_ADDR, ACCEL_ZOUT_H, 2)

    # Convert the raw accelerometer data to acceleration in m/s^2
    accel_x = int.from_bytes(accel_x_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81
    accel_y = int.from_bytes(accel_y_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81
    accel_z = int.from_bytes(accel_z_raw, byteorder='big', signed=True) / AFS_SEL_SENSITIVITY[0] * 9.81

    #Calculates the sum of all vectors
    accel_sum = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)



    # Print the acceleration in m/s^2
    print("Acceleration in X direction: ", round(accel_x, 2), "m/s^2")
    print("Acceleration in Y direction: ", round(accel_y, 2), "m/s^2")
    print("Acceleration in Z direction: ", round(accel_z, 2), "m/s^2")
    print("Acceleration: ", round(accel_sum, 2), "m/s^2")
    
   # time.sleep(1)
