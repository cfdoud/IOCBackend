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

# Connect to Wi-Fi
def connect_to_wifi(ssid1, password1):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid1, password1)
    while not wlan.isconnected():
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

# Capture sequence: Turn on LEDs, send capture command to DVR, and turn off LEDs
def capture_sequence():
    print("Starting capture sequence...")
    # Turn on the first set of LEDs (white)
    led_set_1.on()
    print("LED set 1 on")
    send_snapshot_command()  # Send command to DVR to take the first snapshot
    time.sleep(0.8)  # Precise exposure time of 0.8 seconds
    led_set_1.off()  # Turn off the first set of LEDs
    print("LED set 1 off")

    # Minimal delay between the two captures
    time.sleep(0.01)  # Adjust if needed for your DVR timing
 
    # Turn on the second set of LEDs (violet)
    led_set_2.on()
    print("LED set 2 on")
    send_snapshot_command()  # Send command to DVR to take the second snapshot
    time.sleep(0.8)  # Precise exposure time of 0.8 seconds
    led_set_2.off()  # Turn off the second set of LEDs
    print("LED set 2 off")

# Send HTTP request to trigger screenshot capture in React app
def trigger_screenshot():
    try:
        #url = "http://192.168.1.232:5000/trigger-screenshot"
        url = "http://iocserver.paracontechnologies.com:8080/screenshot"
        response = urequests.get(url)
        print('Server Response:', response.text)
        response.close()
    except Exception as e:
        print("Failed to send request:", e)


# Main loop: Check for button press and trigger capture sequence
print('start')
SSID1 = 'serial_lain'
PASSWORD1 = 'GoGoGoZeppeli'
connect_to_wifi(SSID1, PASSWORD1)

while True:
    if button.value():  # Check if the button is pressed
        #capture_sequence()  # Trigger the capture sequence
        print("button pressed")
        trigger_screenshot()  # Send HTTP request to server to trigger screenshot

    time.sleep(0.1)  # Small delay to debounce the button

