import smbus2
import time

# I2C address of the ICM20600
address = 0x69

# I2C bus number on the Rock Pi 4
bus_number = 7

# Create an smbus object for the bus number
bus = smbus2.SMBus(bus_number)

def i2c_write_byte(address, register, value):
    bus.write_byte_data(address, register, value)

#Wake up the sensor and select clock source
i2c_write_byte(0x69, 0x6b, 0x01);

#Configure sampling rates fpr accel. and gyro
i2c_write_byte(0x69, 0x1d, 0x10);
#i2c_write_byte(0x69, GYRO_CONFIG, 0x18);

#Enable accel. and gyro
i2c_write_byte(0x69, 0x6c, 0x00);

# ICM20600 register addresses for reading accelerometer data
reg_x_accel = 0x20
reg_y_accel = 0x21
reg_z_accel = 0x22



# Read accelerometer data
while True:
    # Read the raw accelerometer data
    accel_x = bus.read_byte_data(address, reg_x_accel)
    accel_y = bus.read_byte_data(address, reg_y_accel)
    accel_z = bus.read_byte_data(address, reg_z_accel)

    # Convert the raw data to G-forces
    accel_x_g = accel_x / 16384.0
    accel_y_g = accel_y / 16384.0
    accel_z_g = accel_z / 16384.0

    # Print the accelerometer data
    print("Accelerometer (G): X = %.2f, Y = %.2f, Z = %.2f" % (accel_x_g, accel_y_g, accel_z_g))

    # Wait for some time before reading again
    time.sleep(0.1)
    
    
