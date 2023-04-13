#SDA_Pin = 71 #pin nr 3
#SCL_Pin = 72 # pin nr 5
import smbus2
import time

# I2C address of ICM20600
ICM20600_ADDRESS = 0x69

# Initialize I2C bus
bus = smbus2.SMBus(7)

# Read acceleration values
def read_acceleration():
    accel_x = bus.read_word_data(ICM20600_ADDRESS, 0x3B)
    accel_y = bus.read_word_data(ICM20600_ADDRESS, 0x3D)
    accel_z = bus.read_word_data(ICM20600_ADDRESS, 0x3F)
    return (accel_x, accel_y, accel_z)

# Read gyro values
def read_gyro():
    gyro_x = bus.read_word_data(ICM20600_ADDRESS, 0x43)
    gyro_y = bus.read_word_data(ICM20600_ADDRESS, 0x45)
    gyro_z = bus.read_word_data(ICM20600_ADDRESS, 0x47)
    return (gyro_x, gyro_y, gyro_z)

# Read temperature value
def read_temperature():
    temp = bus.read_word_data(ICM20600_ADDRESS, 0x41)
    return temp

while True:
    accel = read_acceleration()
    gyro = read_gyro()
    temp = read_temperature()
    print("Acceleration:", accel, "Gyro:", gyro, "Temperature:", temp)
    time.sleep(0.5)
