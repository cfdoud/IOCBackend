import network
import urequests
from machine import Pin
import usocket as socket
import time

# Initialize GPIO pins for the two sets of LEDs
led_set_1 = Pin(15, Pin.OUT)  # First set of LEDs (white)
led_set_2 = Pin(16, Pin.OUT)  # Second set of LEDs (violet)

# Initialize the button with a pull-down resistor
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

# State variables
capture_stage = 0  # 0: idle, 1: first LED on, 2: waiting for first capture, 3: second LED on, 4: waiting for second capture

# Connect to Wi-Fi
def connect_to_wifi(ssid1, password1):
    print(ssid1, password1)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    wlan.connect(ssid1, password1)
    
    while not wlan.isconnected():
        print("hello")
        time.sleep(1)  # Small delay to avoid busy waiting
    
    print('Connected to Wi-Fi')
    print('IP Address:', wlan.ifconfig()[0])  # Print the IP address assigned to the Pico W

# Send API command to DVR for snapshot
def send_snapshot_command():
    host = "192.168.1.254"  # DVR's IP address
    port = 8181  # DVR's port for commands
    telnet_command = "killall -32 rcS\n"  # Command to take a snapshot
   
    try:
        # Create a socket connection to the DVR
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print("sending my snapshot")
        # Send the snapshot command
        s.send(telnet_command.encode('utf-8'))

        # Receive response (if any)
        response = s.recv(1024)
        print('DVR Response:', response.decode('utf-8'))

        # Close the connection
        s.close()
    except Exception as e:
        print("Failed to send snapshot command:", e)

# Send HTTP request to trigger screenshot capture in React app
def trigger_screenshot():
    try:
        #url = "http://iocserver.paracontechnologies.com:8080/screenshot"
        url = "http://35.173.205.52:8080/screenshot"
        #url = "http://98.83.176.205:5001/screenshot"
        print("next phase")
        response = urequests.get(url)
        response.close()
    except Exception as e:
        print("Failed to send request:", e)

# Main loop: Check for button press and trigger capture sequence
print('start')

SSID1 = 'Cove'
PASSWORD1 = 'sandy.toes'
connect_to_wifi(SSID1, PASSWORD1)

while True:
    
    if button.value() and capture_stage == 0:  # Check if the button is pressed and in idle state
        print("button pressed")
        capture_stage = 1  # Move to the first LED stage

    # State machine to manage LED capture sequence
    if capture_stage == 1:
        print('led1')
        led_set_1.on()  # Turn on the first set of LEDs
        time.sleep(0.1)  # Small delay to ensure LED is on before capturing
        trigger_screenshot()  # Send command to capture the first screenshot
        time.sleep(1.5)  # Wait for the exposure time
        led_set_1.off()  # Turn off the first set of LEDs
        capture_stage = 2  # Move to the waiting stage before second LED

    elif capture_stage == 2:
        time.sleep(0.5)  # Wait before turning on the second LED
        capture_stage = 3  # Move to the second LED stage

    elif capture_stage == 3:
        print('led2')
        led_set_2.on()  # Turn on the second set of LEDs
        time.sleep(0.1)  # Small delay to ensure LED is on before capturing
        trigger_screenshot()  # Send command to capture the second screenshot
        time.sleep(0.8)  # Wait for the exposure time
        led_set_2.off()  # Turn off the second set of LEDs
        capture_stage = 0  # Reset to idle state
        print("Capture sequence finished")

    time.sleep(0.1)  # Small delay for main loop to prevent busy waiting


