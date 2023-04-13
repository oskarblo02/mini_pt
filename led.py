from periphery import GPIO
import time
LED_Pin=73
LED_GPIO=GPIO(LED_Pin,"out")
while True:
    try:         
        LED_GPIO.write(True)
        print("LED ON!")
        time.sleep(1)
        LED_GPIO.write(False)
        print("LED OFF!")
        time.sleep(1)
    except KeyboardInterrupt:
        LED_GPIO.write(False)
        break
    except IOError:
        print("error")
        
LED_GPIO.close()
