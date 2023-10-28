import board
import digitalio
import usb_hid
import rotaryio
from hid_gamepad.simple import Gamepad

gp = Gamepad(usb_hid.devices)

# Create some buttons. The physical buttons are connected
# to ground on one side and these pins on the other.
button_pins = (board.GP11,)

# Map the buttons to button numbers on the Gamepad.
# gamepad_buttons[i] will send that button number when buttons[i]
# is pushed.
gamepad_buttons = (1,)

buttons = [digitalio.DigitalInOut(pin) for pin in button_pins]
for button in buttons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

enc_1 = rotaryio.IncrementalEncoder(board.GP9, board.GP10)
enc_2 = rotaryio.IncrementalEncoder(board.GP13, board.GP14)
enc_3 = rotaryio.IncrementalEncoder(board.GP7, board.GP8)
enc_4 = rotaryio.IncrementalEncoder(board.GP3, board.GP4)

encoders = (enc_1, enc_2, enc_3, enc_4)

# Define gamepad buttons for encoder positions
encoder_buttons = [(2, 3), (4, 5), (6, 7), (8, 9)]

last_positions = [None] * len(encoders)

while True:
    # Buttons are grounded when pressed (.value = False).
    for i, button in enumerate(buttons):
        gamepad_button_num = gamepad_buttons[i]
        if button.value:
            gp.release_buttons(gamepad_button_num)
            print(" release", gamepad_button_num, end="")
        else:
            gp.press_buttons(gamepad_button_num)
            print(" press", gamepad_button_num, end="")

    # Read and print rotary encoder positions and toggle between buttons based on position
    for i, encoder in enumerate(encoders):
        position = encoder.position
        last_position = last_positions[i]
        if last_position is None or position != last_position:
            print(f"Encoder {i + 1}: {position}")
            last_positions[i] = position
            # Release both buttons
            gp.release_buttons(encoder_buttons[i][0])
            gp.release_buttons(encoder_buttons[i][1])
            # Determine which button to press based on position
            if 0 <= position < len(encoder_buttons[i]):
                button_to_press = encoder_buttons[i][position]
                gp.press_buttons(button_to_press)
