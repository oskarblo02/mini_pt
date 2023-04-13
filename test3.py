import smbus2
import time

# I2C address of the ICM20600 sensor
ICM20600_ADDR = 0x69

# Register addresses for the accelerometer configuration
ACCEL_CONFIG = 0x1C

# Initialize I2C bus and open a connection to the ICM20600 sensor
bus = smbus2.SMBus(7)
bus.write_byte_data(ICM20600_ADDR, 0x6B, 0x00)

# Read the AFS_SEL value from the ACCEL_CONFIG register
afs_sel = (bus.read_byte_data(ICM20600_ADDR, ACCEL_CONFIG) & 0b00011000) >> 3

# Print the AFS_SEL value and the corresponding sensitivity in LSB/g
print("AFS_SEL value: ", afs_sel)
if afs_sel == 0:
    sensitivity = 16384
elif afs_sel == 1:
    sensitivity = 8192
elif afs_sel == 2:
    sensitivity = 4096
elif afs_sel == 3:
    sensitivity = 2048
print("Accelerometer sensitivity: ", sensitivity, "LSB/g")
