import network
import urequests
from machine import Pin, PWM
import time

# Initialize PWM for the two sets of LEDs
led_set_1 = PWM(Pin(16))  # First set of LEDs (white)
led_set_2 = Pin(15, Pin.OUT)  # Second set of LEDs (violet)

# Set the PWM frequency (in Hz)
led_set_1.freq(1000)  # Set frequency to 1 kHz for the first LED
#led_set_2.freq(1000)  # Set frequency to 1 kHz for the second LED

# Initialize the button with a pull-down resistor
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

# State variables
capture_stage = 0  # 0: idle, 1: first LED on, 2: waiting for first capture, 3: second LED on, 4: waiting for second capture

# Connect to Wi-Fi
def connect_to_wifi(ssid1, password1):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid1, password1)
    
    while not wlan.isconnected():
        time.sleep(1)  # Small delay to avoid busy waiting
    
    print('Connected to Wi-Fi')
    print('IP Address:', wlan.ifconfig()[0])  # Print the IP address assigned to the Pico W

# Send HTTP request to trigger screenshot capture in React app
def trigger_screenshot():
    try:
        url = "http://35.173.205.52:8080/screenshot"
        print("Attempting to send request to:", url)
        
        response = urequests.get(url, timeout=5)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        
        response.close()
        print("Request successfully sent")
    except Exception as e:
        print("Failed to send request:", e)

# Main loop
print('start')

#SSID1 = 'Cove Resident'
#PASSWORD1 = 'shore.line'
SSID1 = 'serial_lain'
PASSWORD1 = 'GoGoGoZeppeli'
#connect_to_wifi(SSID1, PASSWORD1)
button_held = False
while True:
    if button.value() and not button_held:  
        print("Button pressed, turning on first LED")
        led_set_1.duty_u16(1315)  
        button_held = True 

    elif not button.value() and button_held:  
        print("Button released, taking first photo")
        #trigger_screenshot()  
        led_set_1.duty_u16(0)
        
        # Second LED sequence
        print("Turning on second LED")
        led_set_2.on()
        #led_set_2.duty_u16(65535)  
        time.sleep(0.8)  
        print("Taking second photo") 
        #trigger_screenshot()
        led_set_2.off()
        #led_set_2.duty_u16(0)
        # Reset button state
        button_held = False  
        print("Capture sequence finished")

    time.sleep(0.1)  # Small delay for main loop to prevent busy waiting