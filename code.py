import board
import analogio
import digitalio
import usb_hid
import rotaryio
import time
from hid_gamepad.simple import Gamepad


# Initialize the Gamepad object using the HID (Human Interface Device) library
gp = Gamepad(usb_hid.devices)


def range_map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

########################################################################
########################################################################

# Function to handle button presses and releases
def handle_buttons():
    for i, button in enumerate(buttons):
        gamepad_button_num = gamepad_buttons[i]
        if button.value:
            gp.release_buttons(gamepad_button_num)
        else:
            gp.press_buttons(gamepad_button_num)


# Define the physical button pins
button_pins = (board.GP11,)

# Map the physical buttons to gamepad button numbers
gamepad_buttons = (1,)

# Initialize digital input objects for the physical buttons
buttons = [digitalio.DigitalInOut(pin) for pin in button_pins]

# Configure the buttons as input with pull-up resistors
for button in buttons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

########################################################################
########################################################################
# Initialize four rotary encoders using specific pins
enc_1 = rotaryio.IncrementalEncoder(board.GP9, board.GP10)
enc_2 = rotaryio.IncrementalEncoder(board.GP13, board.GP14)
enc_3 = rotaryio.IncrementalEncoder(board.GP7, board.GP8)
enc_4 = rotaryio.IncrementalEncoder(board.GP3, board.GP4)
 
encoders = (enc_1, enc_2, enc_3, enc_4)

# Define pairs of gamepad buttons corresponding to encoder positions
encoder_buttons = [(2, 3), (4, 5), (6, 7), (8, 9)]

# Initialize a list to store the last positions of the encoders
last_encoder_positions = [0] * len(encoders)

# Function to handle encoder rotation
def handle_encoders():
    for i, encoder in enumerate(encoders):
        position = encoder.position
        last_position = last_encoder_positions[i]

        if position != last_position:
            direction = "ClockWise" if position > last_position else "CounterClockWise"

            gp.release_buttons(encoder_buttons[i][0])
            gp.release_buttons(encoder_buttons[i][1])

            if direction == "CounterClockWise":
                gp.press_buttons(encoder_buttons[i][0])
                time.sleep(0.1)

            if direction == "ClockWise":
                gp.press_buttons(encoder_buttons[i][1])
                time.sleep(0.1)

            gp.release_buttons(encoder_buttons[i][0])
            gp.release_buttons(encoder_buttons[i][1])

            last_encoder_positions[i] = position

##################################################
########################################################################
########################################################################
potentiometer_1 = analogio.AnalogIn(board.GP28_A2)
# [(input, axis),]
potentiometers = [(potentiometer_1, "z"), ]
def handle_potentiometer():
    x = 0
    y = 0
    z = 0
    r_z = 0
    for i, potentiometer in enumerate(potentiometers):
        # Assuming the potentiometer is connected to pin GP28
        adc_value = potentiometer[i].value
        # volt = (3.3/65535)*adc_value
        # print(volt)
        
        if(potentiometers[i][1] == "x"):
            x = adc_value
        if(potentiometers[i][1] == "y"):
            y = adc_value
        if(potentiometers[i][1] == "z"):
            z = adc_value
        if(potentiometers[i][1] == "r_z"):
            r_z = adc_value
        # return percentPot

    # Convert range[0, 65535] to -127 to 127
    gp.move_joysticks(
        x=range_map(x, 0, 65535, -127, 127),
        y=range_map(y, 0, 65535, -127, 127),
        z=range_map(z, 0, 65535, -127, 127),
        r_z=range_map(r_z, 0, 65535, -127, 127),
    )
    time.sleep(0.1)

########################################################################
########################################################################
hall_toggle_1 = digitalio.DigitalInOut(board.GP15)
# [(input, button),]
hall_toggles = [(hall_toggle_1, 2),]


def handle_hall_effect_sensor_toggle():
    # Create an 'object' for our Hall Effect Sensor
    # When sensor is near magnet, signal is pulled to zero volts
    for i, hall_toggle in enumerate(hall_toggles):
        hall_toggle[i].direction = digitalio.Direction.INPUT
        hall_toggle[i].pull = digitalio.Pull.UP
        # print(str(hall_effect_sensor_toggle.value) + " handle_hall_effect_sensor_toggle")

        if hall_toggle[i].value == True:
            gp.release_buttons(hall_toggles[i][1])
        if hall_toggle[i].value == False:    
            gp.press_buttons(hall_toggles[i][1])



########################################################################
########################################################################
hall_linear_1 = analogio.AnalogIn(board.GP27_A1)
# [(input, button),]
hall_linear_toggles = [(hall_linear_1, 3),]

def handle_hall_effect_sensor_linear_toggle():
    # Assuming the potentiometer is connected to pin GP27
    # 49E LINEAR HALL-EFFECT SENSOR 
    for i, hall_linear_toggle in enumerate(hall_linear_toggles):

        adc_value = hall_linear_toggle[i].value
        volt = (3.3/65535)*adc_value
 
        # maped = range_map(volt, 0, 3.3, -127, 127)
        maped = range_map(volt, 0.88, 2.67, -127, 127)
        result = closer_to_value(maped, -127, 0, 127)
        # print("The value "+ str(maped)+ " is closer to:", result)

        if result < 0:
            # print("press")
            gp.press_buttons(hall_linear_toggles[i][1])
        elif result > 0:  
            # print("press")
            gp.press_buttons(hall_linear_toggles[i][1])
        else:
            # print("release")
            gp.release_buttons(hall_linear_toggles[i][1])

########################################################################
########################################################################

def closer_to_value(value, ref_minus, ref_center, ref_plus):
    # Calculate the absolute differences
    diff1 = abs(value - ref_minus)
    diff2 = abs(value - ref_center)
    diff3 = abs(value - ref_plus)

    # Compare the differences and determine which reference value is closer
    if diff1 < diff2 and diff1 < diff3:
        return ref_minus
    elif diff2 < diff1 and diff2 < diff3:
        return ref_center
    elif diff3 < diff1 and diff3 < diff2:
        return ref_plus
    else:
        # If differences are equal or some other condition, you can handle it accordingly
        return ref_center


########################################################################
########################################################################

# Main loop
while True:
    handle_buttons()
    handle_encoders()
    handle_potentiometer()
    handle_hall_effect_sensor_toggle()
    handle_hall_effect_sensor_linear_toggle()
    # time.sleep(0.5)


# todo add incremental encoder.. with fixed number of positions that wraps around  

