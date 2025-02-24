import numpy as np
import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *

###############################################################################
# SPRITE DEFINITIONS
###############################################################################
def resample_trace(x, y, points=200):
    """
    Resample (x,y) to 'points' samples for a smoother waveform on the scope.
    """
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def get_character_pulse(points=200):
    """
    A simple square ~±0.5 in x,y before scaling.
    """
    xy = [
       (-0.2, -0.3),
        (-0.5, -0.5),
        (-0.8, -0.3),
        (-1, 0),
        (-0.8, 0.3),
        (-0.5, 0.5),
        (-0.2, 0.3),
        (0, 0),
        (-0.2, -0.3),
        (-0.5, 0),
        (0, -0.5),
        (0.25, 0.5),
        (0.5, -0.5),
        (0.75, 0.5),
        (1, -0.5),
    ]
    x_vals = [p[0] for p in xy]
    y_vals = [p[1] for p in xy]
    return resample_trace(x_vals, y_vals, points)

def get_floor_pulse(points=200):
    """
    A rectangular floor shape ~±1 in x, 0..0.2 in y.
    """
    xy = [
        (-1.0, 0),
        (-1.0, 0.2),
        ( 1.0, 0.2),
        ( 1.0, 0),
        (-1.0, 0),
    ]
    x_vals = [p[0] for p in xy]
    y_vals = [p[1] for p in xy]
    return resample_trace(x_vals, y_vals, points)

###############################################################################
# QUA CONFIGURATION
###############################################################################
SPRITE_LENGTH = 16500
CHAR_SCALE = 0.1   # The character will be ±0.05 in each direction
FLOOR_SCALE = 0.3  # The floor is ±0.3 in X, 0..0.06 in Y

char_raw = get_character_pulse(SPRITE_LENGTH)
floor_raw = get_floor_pulse(SPRITE_LENGTH)

char_x = (char_raw[0] * CHAR_SCALE).tolist()
char_y = (char_raw[1] * CHAR_SCALE).tolist()

floor_x = (floor_raw[0] * FLOOR_SCALE).tolist()
floor_y = (floor_raw[1] * FLOOR_SCALE).tolist()

configuration = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1000",
            "fems": {
                5: {
                    "type": "LF",
                    "analog_outputs": {i: {"offset": 0.0} for i in range(1, 8)},
                    "analog_inputs": {},
                    "digital_outputs": {i: {} for i in range(1, 8)},
                }
            },
        }
    },
    "elements": {
        "screen": {
            "mixInputs": {
                "I": ("con1", 5, 5),
                "Q": ("con1", 5, 6),
            },
            "intermediate_frequency": 0,
            "operations": {
                "character": "character_pulse",
                "floor": "floor_pulse",
            },
        },
        'draw_marker_element': {
            'singleInput': {
                'port': ('con1', 5, 1),
            },
            'intermediate_frequency': 0,
            'operations': {
                "marker_pulse": "marker_pulse",
            },
        },
    },
    "pulses": {
        "character_pulse": {
            "operation": "control",
            "length": SPRITE_LENGTH,
            "waveforms": {"I": "char_x", "Q": "char_y"},
        },
        "floor_pulse": {
            "operation": "control",
            "length": SPRITE_LENGTH,
            "waveforms": {"I": "floor_x", "Q": "floor_y"},
        },
            "marker_pulse": {
            "operation": "control",
            'length': SPRITE_LENGTH,
            'waveforms': {"single": "marker_wf"},
        },
    },
    "waveforms": {
        "char_x": {
            "type": "arbitrary",
            "samples": char_x,
        },
        "char_y": {
            "type": "arbitrary",
            "samples": char_y,
        },
        "floor_x": {
            "type": "arbitrary",
            "samples": floor_x,
        },
        "floor_y": {
            "type": "arbitrary",
            "samples": floor_y,
        },
        'marker_wf': {"type": "constant", "sample": 0.2},
    },
}

def move_cursor(x, y):
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)

def draw_sprite(name, x, y):
    move_cursor(x, y)
    play(name, "screen")

def draw_character(x, y):
    draw_sprite("character", x, y)

def draw_floor(x, y):
    draw_sprite("floor", x, y)

###############################################################################
# MAIN QUA PROGRAM
###############################################################################
import random

N_FLOORS = 3
FIELD_SIZE = 0.5   # must remain within ±0.5 total
TIME_STEP_SIZE = 0.0025
WAIT_TIME = 2e6    # ns wait each frame
GRAVITY = 0.5
JUMP_FORCE = 0.1
CHAR_SPEED = 0.1
CHAR_RADIUS = 0.05  # half the bounding box side
SCROLL_SPEED = 0.2

qmm = QuantumMachinesManager("172.16.33.107",9510)
qm = qmm.open_qm(configuration)

# 1. Generate floors so they don't overlap each other in X
#    e.g., place them from x= -0.3, -0.1, +0.1, +0.3, etc.
floors_x_positions = []
floors_y_positions = []
start_x = -0.3
for i in range(N_FLOORS):
    x_pos = start_x + i * 0.2  # spacing floors by 0.2 in X
    # random Y in [-0.4, -0.2] for example
    y_pos = random.uniform(-0.4, -0.2)
    floors_x_positions.append(x_pos)
    floors_y_positions.append(y_pos)

# Convert to float for QUA arrays
floors_x_list = [float(x) for x in floors_x_positions]
floors_y_list = [float(y) for y in floors_y_positions]

def get_inputs(move, act):
    """
    Example user input:
    - IO1: 1 => left, 2 => right
    - IO2: 5 => jump, 10 => exit
    """
    assign(move, IO1)
    assign(act, IO2)

with program() as mario_like:
    # Character state
    char_x = declare(fixed, value=0)
    char_y = declare(fixed, value=0)
    char_vy = declare(fixed, value=0)

    # Floors
    # We'll store their positions in QUA arrays
    floors_x = declare(fixed, value=floors_x_list)
    floors_y = declare(fixed, value=floors_y_list)

    # Time
    t = declare(fixed, 0)
    t_prev = declare(fixed, 0)
    dt = declare(fixed, 0)

    move = declare(int, 0)
    act = declare(int, 0)
    cont = declare(bool, True)

    i = declare(int, 0)
    

    with while_(cont):
        assign(dt, t - t_prev)
        assign(t_prev, t)

        # Get inputs
        get_inputs(move, act)

        # Move left or right
        with if_(move == 1):
            assign(char_x, char_x - CHAR_SPEED * dt)
        with if_(move == 2):
            assign(char_x, char_x + CHAR_SPEED * dt)

        # Jump
        with if_(act == 5):
            assign(char_vy, +JUMP_FORCE)
        # Quit
        with if_(act == 10):
            assign(cont, False)

        floor_half_width = 0.3
        floor_height = 0.06  # from 0..0.06 in y
        with for_(i, 0, i < N_FLOORS, i + 1):
            assign(floors_x[i], floors_x[i] - SCROLL_SPEED * dt)
        # Gravity (down is negative)
        assign(char_vy, char_vy - GRAVITY * dt)
        assign(char_y, char_y + char_vy * dt)
 

        # We'll check if the character is above the floor, but not by too much
        for i in range (N_FLOORS):
            # bounding box for the floor
            floor_left   = floors_x[i] - floor_half_width
            floor_right  = floors_x[i] + floor_half_width
            floor_bottom = floors_y[i]
            floor_top    = floors_y[i] + floor_height

            # bounding box for the character
            char_left   = char_x - CHAR_RADIUS
            char_right  = char_x + CHAR_RADIUS
            char_bottom = char_y - CHAR_RADIUS
            char_top    = char_y + CHAR_RADIUS

            # Overlap check
            with if_(
                (char_right  >= floor_left) &
                (char_left   <= floor_right) &
                (char_bottom <= floor_top )
                # (char_top    >= floor_bottom)
            ):
                # If the character is coming from above, we clamp him
                # i.e., if char_bottom was below floor_top but above floor_bottom
                with if_((char_bottom < floor_top) & (char_y > floors_y[i])):
                    # place char_y on top of the floor
                    assign(char_y, floor_top + CHAR_RADIUS)
                    assign(char_vy, 0)

        # Drawing
        # 1) Draw floors
        play("marker_pulse", "draw_marker_element")
        for i in range (N_FLOORS):
            draw_floor(floors_x[i], floors_y[i])

        # 2) Draw character
        draw_character(char_x, char_y)
        align()

        # Wait
        wait(int(WAIT_TIME))
        assign(t, t + TIME_STEP_SIZE)

# =============================================================================
# IO and Main
# =============================================================================
if __name__ == "__main__":
    job = qm.execute(mario_like)
    print("Mario-like platformer started. Press ESC to quit.")

    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                qm.set_io2_value(10)  # exit
                break
            elif event.key == keyboard.KeyCode.from_char('a'):
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io1_value(1)  # left
                else:
                    qm.set_io1_value(0)
            elif event.key == keyboard.KeyCode.from_char('d'):
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io1_value(2)  # right
                else:
                    qm.set_io1_value(0)
            elif event.key == keyboard.KeyCode.from_char('w'):
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io2_value(5)  # jump
                else:
                    qm.set_io2_value(0)
            else:
                pass

    print("Game ended!")
