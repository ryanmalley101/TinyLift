import RPi.GPIO as GPIO
import time
from RPLCD import i2c
import signal
import sys
import smbus2

def signal_handler(sig, frame):
    bus.close()
    GPIO.cleanup()
    sys.exit(0)
    

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# bus = smbus2.SMBus(1)

# Function to handle button press event
def button_pressed(channel):
    global elevator_state, current_floor, call_state, requested_floors

    time.sleep(.1)
    
    if GPIO.input(channel):
        return

    if channel == call_up_button_pin:
        if call_state == cab_states['DOWN'] or call_state == call_states['UPDOWN']:
            call_state = call_states['UPDOWN']
        else:
            call_state = call_states['UP']
    elif channel == call_down_button_pin or call_state == call_states['UPDOWN']:
        if call_state == call_states['UP'] or call_state == call_states['UPDOWN']:
            call_state = call_states['UPDOWN']
        else:
            call_state = call_states['DOWN']
    elif channel in request_button_pins:
        print(f"Floor button {request_button_pins.index(channel)+1} pressed")
        requested_floor = request_button_pins.index(channel) + 1
        if requested_floor not in requested_floors:
            requested_floors.append(requested_floor)
            
    update_led_rings()

# Function to update the LED rings
def update_led_rings():
#     print(f"State LED Call {call_state}")
    for i in range(len(led_ring_pins)):
        GPIO.output(led_ring_pins[i], 1 if (i + 1) in requested_floors else 0)
    if call_state == call_states["UP"]:
#         print("Call State UP LED")
        GPIO.output(call_up_led_pin, 1)
        GPIO.output(call_down_led_pin, 0)
    elif call_state == call_states["DOWN"]:
#         print("Call State DOWN LED")
        GPIO.output(call_up_led_pin, 0)
        GPIO.output(call_down_led_pin, 1)
    elif call_state == call_states["UPDOWN"]:
#         print("Call State UPDOWN LED")
        GPIO.output(call_up_led_pin, 1)
        GPIO.output(call_down_led_pin, 1)
    else:
#         print("Call State NONE LED")
        GPIO.output(call_up_led_pin, 0)
        GPIO.output(call_down_led_pin, 0)
# GPIO pin for the call button to go up (BCM GPIO 17)
call_up_button_pin = 20
call_up_led_pin = 22

# GPIO pin for the call button to go down (BCM GPIO 18)
call_down_button_pin = 21
call_down_led_pin = 23

# GPIO pins for request buttons (BCM GPIOs 27, 22, 23, 24, 25, 4)
request_button_pins = [4, 5, 6, 7, 8, 9]

# GPIO pins for LED rings (BCM GPIOs 2, 3, 8, 7, 10, 9)
led_ring_pins = [10, 11, 12, 13, 14, 15]

# Define elevator states
cab_states = {
    'UP': 1,
    'DOWN': 2,
    'RESTING': 3
}

# Define elevator states
call_states = {
    'UP': 1,
    'DOWN': 2,
    'UPDOWN': 3,
    'NONE': 4
}

# Initialize GPIO
GPIO.setmode(GPIO.BCM)

print(f"Configuring pin {call_up_button_pin}")
print(f"Configuring pin {call_down_button_pin}")
# Setup button, LED pin modes
GPIO.setup(call_up_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(call_down_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(call_up_led_pin, GPIO.OUT)
GPIO.output(call_up_led_pin, 1)
GPIO.setup(call_down_led_pin, GPIO.OUT)
GPIO.output(call_down_led_pin, 1)

for pin in request_button_pins:
    print(f"Configuring pin {pin}")
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in led_ring_pins:
    print(f"Configuring pin {pin}")
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 1)

# Attach button event detection
GPIO.add_event_detect(call_up_button_pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)
GPIO.add_event_detect(call_down_button_pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)
for pin in request_button_pins:
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)

lcdmode = 'i2c'
cols = 20
rows = 4
charmap = 'A00'
i2c_expander = 'PCF8574'

address = 0x27
port = 1

lcd = i2c.CharLCD(i2c_expander, address, port=port,
                  cols=cols, rows=rows)

total_floors = 6
ground_floor = 3
current_floor = 3  # Initialize the current floor to 1
elevator_state = cab_states['RESTING']  # Initialize the elevator state to RESTING
call_state = call_states['NONE']  # Variable to store the call state ('UP' or 'DOWN')
requested_floors = []  # List to store the requested floors
skip_loop = False
print("Starting the loop")
# Main loop
try:
    while True:
        skip_loop = False
        requested_floors.sort()
        time.sleep(2)  # You can adjust the delay as needed based on the elevator speed
        print("")
        update_led_rings()
        # Update the LCD display with current floor and travel direction
#         lcd.clear()
        lcd.clear()
        lcd.write_string(f"Floor {current_floor}")
        lcd.crlf()
        lcd.write_string(f"Direction: ")
        if elevator_state == cab_states['UP']:
            lcd.write_string("UP")
        elif elevator_state == cab_states['DOWN']:
            lcd.write_string("DOWN")
        else:
            lcd.write_string("HOLD")
        print(f"Current Floors {current_floor}")
        print(f"Call State {call_state}")
        print(f"Requested Floor {requested_floors}")
        if (current_floor == ground_floor and call_state != call_states['NONE']):
            call_state = call_states['NONE']
            time.sleep(2)
            continue
        if elevator_state == cab_states['UP']:
            print("Elevator Going Up")
            if (current_floor == total_floors):
                elevator_state = cab_states['RESTING']
            if (current_floor + 1 in requested_floors):
                current_floor += 1
                requested_floors.remove(current_floor)
                time.sleep(2)
                continue
            for floor in range(current_floor + 1, total_floors+1):
                if floor in requested_floors:
                    # If theres a requested floor above us and we're already going up
                    # just keep going up
                    current_floor += 1
                    skip_loop = True
                    break
            if skip_loop:
                continue

            for floor in range (0, current_floor):
                if floor in requested_floors:
                    elevator_state = cab_states['DOWN'] 
                    break
            if call_state != call_states['NONE'] and requested_floors == []:
                print("No requested floors, ground floor call button pressed")
                if current_floor > ground_floor:
                    current_floor -= 1
                    elevator_state = cab_states['DOWN']
                    time.sleep(2)
                    continue
                elif current_floor < ground_floor:
                    current_floor += 1
                    elevator_state = cab_states['UP']
                    time.sleep(2)
                    continue
                else:
                    call_state = call_states['NONE']
                    elevator_state = cab_states['RESTING']
            if call_state == call_states['NONE'] and requested_floors == []:
                elevator_state = cab_states['RESTING']
                
        elif elevator_state == cab_states['DOWN']:
            print("Elevator Going Down")
            if (current_floor == 1):
                elevator_state = cab_states['RESTING']
            if (current_floor - 1 in requested_floors):
                current_floor -= 1
                requested_floors.remove(current_floor)
                time.sleep(2)
                continue
            for floor in range(0, current_floor):
                if floor in requested_floors:
                    # If theres a requested floor above us and we're already going down
                    # just keep going up
                    current_floor -= 1
                    skip_loop = True
                    break
            if skip_loop:
                continue
            for floor in range (current_floor, total_floors+1):
                if floor in requested_floors:
                    elevator_state = cab_states['UP']
                    break
            if call_state != call_states['NONE'] and requested_floors == []:
                if current_floor > ground_floor:
                    current_floor -= 1
                    elevator_state = cab_states['DOWN']
                    continue
                elif current_floor < ground_floor:
                    current_floor += 1
                    elevator_state = cab_states['UP']
                    continue
                else:
                    call_state = call_states['NONE']
                    elevator_state = cab_states['RESTING']
            if call_state == call_states['NONE'] and requested_floors == []:
                elevator_state = cab_states['RESTING']
        else:
            print("Elevator Stationary")
            if (current_floor == ground_floor):
                if (call_state != call_states['NONE']):
                    call_state = call_states['NONE']
                    time.sleep(2)
                    continue
            if call_state != call_states['NONE']:
                if current_floor > ground_floor:
                    elevator_state = cab_states['DOWN']
                else:
                    elevator_state = cab_states['UP']
            else:
                for floor in range (0, total_floors+1):
                    if floor in requested_floors:
                        if floor < current_floor:
                            elevator_state = cab_states['DOWN']
                            break
                        elif floor > current_floor:
                            elevator_state = cab_states['UP']
                            break
                        else:
                            requested_floors.remove(floor)
                            time.sleep(2)

except KeyboardInterrupt:
    lcd.close()  # Clear the display before exiting
    GPIO.cleanup()  # Cleanup GPIO settings
    
