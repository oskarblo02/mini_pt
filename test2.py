import smbus2
import time
import math

# I2C address of the ICM-20600 sensor
ICM20600_ADDRESS = 0x69

# Register addresses
PWR_MGMT_1 = 0x6B
PWR_MGMT_2 = 0x6C
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_L = 0x40
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
GYRO_XOUT_L = 0x44
GYRO_YOUT_L = 0x46
GYRO_ZOUT_L = 0x48
ACCEL_CONFIG = 0x1D
GYRO_CONFIG = 0x1B


# I2C bus number
I2C_BUS = 7

# Initialize the I2C bus and create an SMBus object
bus = smbus2.SMBus(I2C_BUS)

SENSITIVITY = 16384.0  
GRAVITY = 9.82

# Function for writing a byte to a register over I2C
def i2c_write_byte(address, register, value):
    bus.write_byte_data(address, register, value)
    
#Converts raw data to m/s^2
def acc_raw_to_ms2(raw_data):
    ms2 = (raw_data / SENSITIVITY) * GRAVITY
    return (ms2)

# Wake up the sensor and select the clock source
i2c_write_byte(ICM20600_ADDRESS, PWR_MGMT_1, 0x01)

# Set the accelerometer and gyroscope full-scale ranges and sampling rates
i2c_write_byte(ICM20600_ADDRESS, ACCEL_CONFIG, 0x10)
i2c_write_byte(ICM20600_ADDRESS, GYRO_CONFIG, 0x18)

# Enable the accelerometer and gyroscope
i2c_write_byte(ICM20600_ADDRESS, PWR_MGMT_2, 0x00)

# Read and print the raw accelerometer and gyroscope data
while True:
    # Read the raw accelerometer data
    accel_x = (bus.read_byte_data(ICM20600_ADDRESS, ACCEL_XOUT_H) << 8) | bus.read_byte_data(ICM20600_ADDRESS, ACCEL_XOUT_L)
    accel_y = (bus.read_byte_data(ICM20600_ADDRESS, ACCEL_YOUT_H) << 8) | bus.read_byte_data(ICM20600_ADDRESS, ACCEL_YOUT_L)
    accel_z = (bus.read_byte_data(ICM20600_ADDRESS, ACCEL_ZOUT_H) << 8) | bus.read_byte_data(ICM20600_ADDRESS, ACCEL_ZOUT_L)

    # Read the raw gyroscope data
    gyro_x = (bus.read_byte_data(ICM20600_ADDRESS, GYRO_XOUT_H) << 8) | bus.read_byte_data(ICM20600_ADDRESS, GYRO_XOUT_L)
    gyro_y = (bus.read_byte_data(ICM20600_ADDRESS, GYRO_YOUT_H) << 8) | bus.read_byte_data(ICM20600_ADDRESS, GYRO_YOUT_L)
    gyro_z = (bus.read_byte_data(ICM20600_ADDRESS, GYRO_ZOUT_H) << 8) | bus.read_byte_data(ICM20600_ADDRESS, GYRO_ZOUT_L)
    
    #Converts raw data to m/s^2
    x_ms2 = acc_raw_to_ms2(accel_x)
    y_ms2 = acc_raw_to_ms2(accel_y)
    z_ms2 = acc_raw_to_ms2(accel_z)
    
    #Calculates the sum of all vectors
    accel_sum = math.sqrt(x_ms2**2 + y_ms2**2 + z_ms2**2)
    
    # Print the raw data
    #print(f"Accelerometer (raw): X={accel_x}, Y={accel_y}, Z={accel_z}")
    #print(f"Gyroscope (raw): X={gyro_x}, Y={gyro_y}, Z={gyro_z}")
    
    #Print data in m/s^2
    print(f"Accelerometer (m/s^2): X={x_ms2}, Y={y_ms2}, Z={z_ms2}")
    print(f"Vector sum: %.2f ms^2" % accel_sum)
    
    # Wait for 1 second
    time.sleep(1)
