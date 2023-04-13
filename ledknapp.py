from periphery import GPIO
import time
LED_Pin=73      #GPIO pin 73 physical pin 31
Button_Pin=154  #GPIO pin 154 physical pin 16
LED_GPIO=GPIO(LED_Pin,"out")
BUTTON_GPIO=GPIO(Button_Pin,"in")

while True:
    try:   
        buttonvalue=BUTTON_GPIO.read()
        print(buttonvalue)      
        if (buttonvalue==True):
            print("LED ON!")
            LED_GPIO.write(True)
        else:
            LED_GPIO.write(False)
            print("LED OFF!")
    except KeyboardInterrupt:
        LED_GPIO.write(False)
        break
    except IOError:
        print("error")
        
LED_GPIO.close()
