# Import necessary libraries/modules
import board
import digitalio
import usb_hid
import rotaryio
import time
from hid_gamepad.simple import Gamepad

# Initialize the Gamepad object using the HID (Human Interface Device) library
gp = Gamepad(usb_hid.devices)

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

# Initialize four rotary encoders using specific pins
enc_1 = rotaryio.IncrementalEncoder(board.GP9, board.GP10)
enc_2 = rotaryio.IncrementalEncoder(board.GP13, board.GP14)
enc_3 = rotaryio.IncrementalEncoder(board.GP7, board.GP8)
enc_4 = rotaryio.IncrementalEncoder(board.GP3, board.GP4)

encoders = (enc_1, enc_2, enc_3, enc_4)

# Define pairs of gamepad buttons corresponding to encoder positions
encoder_buttons = [(2, 3), (4, 5), (6, 7), (8, 9)]

# Initialize a list to store the last positions of the encoders
last_positions = [0] * len(encoders)

# Main loop
while True:
    # Check the status of physical buttons
    for i, button in enumerate(buttons):
        gamepad_button_num = gamepad_buttons[i]
        if button.value:
            gp.release_buttons(gamepad_button_num)
            # print(" release", gamepad_button_num)
        else:
            gp.press_buttons(gamepad_button_num)
            # print(" press", gamepad_button_num)

    # Read and print rotary encoder positions and toggle between buttons based on position
    for i, encoder in enumerate(encoders):
        position = encoder.position  # Read the current position of the encoder
        last_position = last_positions[i]

        # Check if the position has changed
        if position != last_position:
            # Determine the direction of rotation
            direction = "ClockWise" if position > last_position else "CounterClockWise"
            # print(f"Encoder {i + 1}: {position} ({direction})")

            # Release both buttons associated with this encoder
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

            # Update the last known position for this encoder
            last_positions[i] = position


