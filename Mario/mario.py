import numpy as np
import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *

# =============================================================================
# 1. Sprite Definitions
# =============================================================================
def resample_trace(x, y, points=100):
    """
    Resample the trace defined by x and y to 'points' number of samples.
    """
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def get_mario_pulse(points=100):
    """
    A very simple shape for "Mario": a small circle-like loop.
    Increase the number of points or detail for a better shape.
    """
    t = np.linspace(0, 2*np.pi, 12)
    r = 0.4
    x = r * np.cos(t)
    y = r * np.sin(t)
    return resample_trace(x, y, points)

def get_ground_pulse(points=100):
    """
    A simple horizontal rectangle to represent the ground.
    """
    xy = [
        (-1, 0),  # left bottom
        (-1, 0.3), # left top
        ( 1, 0.3), # right top
        ( 1, 0),   # right bottom
        (-1, 0),   # close the shape
    ]
    x_vals = [p[0] for p in xy]
    y_vals = [p[1] for p in xy]
    return resample_trace(x_vals, y_vals, points)

# =============================================================================
# 2. QUA Configuration
# =============================================================================
FIELD_SIZE = 0.3      # overall field scaling
SPRITE_LENGTH = 100
MARIO_SCALE = 0.12
GROUND_SCALE = 0.3

configuration = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1000",
            "fems": {
                5: {
                    "type": "LF",
                    "analog_outputs": {i: {"offset": 0.0} for i in range(1, 9)},
                    "analog_inputs": {
                        1: {"offset": 0.0, "gain_db": 0},
                        2: {"offset": 0.0, "gain_db": 0},
                    },
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
            "digitalInputs": {
                "draw_marker": {
                    "port": ("con1", 5, 1),
                    "delay": 0,
                    "buffer": 0,
                }
            },
            "operations": {
                "mario": "mario",
                "ground": "ground",
            },
        },
        "draw_marker_element": {
            "singleInput": {
                "port": ("con1", 5, 3),
            },
            "intermediate_frequency": 0,
            "operations": {
                "marker_pulse": "marker_pulse",
            },
        },
    },
    "pulses": {
        "mario": {
            "operation": "control",
            "length": SPRITE_LENGTH,
            "waveforms": {"I": "mario_x", "Q": "mario_y"},
        },
        "ground": {
            "operation": "control",
            "length": SPRITE_LENGTH,
            "waveforms": {"I": "ground_x", "Q": "ground_y"},
        },
        "marker_pulse": {
            "operation": "control",
            "length": 16,
            "waveforms": {"single": "marker_wf"},
        },
    },
    "waveforms": {
        # Mario
        "mario_x": {
            "type": "arbitrary",
            "samples": (
                get_mario_pulse(SPRITE_LENGTH)[0] * FIELD_SIZE * MARIO_SCALE
            ).tolist(),
        },
        "mario_y": {
            "type": "arbitrary",
            "samples": (
                get_mario_pulse(SPRITE_LENGTH)[1] * FIELD_SIZE * MARIO_SCALE
            ).tolist(),
        },
        # Ground
        "ground_x": {
            "type": "arbitrary",
            "samples": (
                get_ground_pulse(SPRITE_LENGTH)[0] * FIELD_SIZE * GROUND_SCALE
            ).tolist(),
        },
        "ground_y": {
            "type": "arbitrary",
            "samples": (
                get_ground_pulse(SPRITE_LENGTH)[1] * FIELD_SIZE * GROUND_SCALE
            ).tolist(),
        },
        # Marker
        "marker_wf": {
            "type": "constant",
            "sample": 0.2
        },
    },
}

# =============================================================================
# 3. Utility Functions for Drawing
# =============================================================================
def move_cursor(x, y):
    """
    Set the DC offsets for the 'screen' element to position the 'cursor'.
    """
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)

def draw_sprite(name, x, y):
    move_cursor(x, y)
    play(name, "screen")

def draw_mario(x, y):
    draw_sprite("mario", x, y)

def draw_ground(x, y):
    draw_sprite("ground", x, y)

# =============================================================================
# 4. Main QUA Program
# =============================================================================

# Game parameters
TIME_STEP_SIZE = 0.01
WAIT_TIME = 2e6    # ns to wait after each frame (adjust for speed)
GRAVITY = 0.05
JUMP_FORCE = 0.3
MARIO_SPEED = 0.15

# Ground collision height
GROUND_LEVEL = 0.0  # We'll define the "floor" at Y=0 in this example

qmm = QuantumMachinesManager("172.16.33.107",9510)
qm = qmm.open_qm(configuration)

def get_inputs(move, act):
    """
    Example user input:
    - IO1: 1 => left, 2 => right
    - IO2: 5 => jump, 10 => exit
    """
    assign(move, IO1)
    assign(act, IO2)

with program() as mario_game:
    # Mario state
    mario_x = declare(fixed, 0)   # Start at X=0
    mario_y = declare(fixed, -0.5)  # Start a bit below center
    mario_vy = declare(fixed, 0)

    # Time
    t = declare(fixed, 0)
    t_prev = declare(fixed, 0)
    dt = declare(fixed, 0)

    # Input
    move = declare(int, 0)
    act = declare(int, 0)

    cont = declare(bool, True)

    with while_(cont):
        assign(dt, t - t_prev)
        assign(t_prev, t)

        # Read inputs
        get_inputs(move, act)

        # Horizontal movement
        with if_(move == 1):
            # Move left
            assign(mario_x, mario_x - MARIO_SPEED * dt)
        with if_(move == 2):
            # Move right
            assign(mario_x, mario_x + MARIO_SPEED * dt)

        # Jump
        with if_(act == 5):
            # Apply upward impulse
            assign(mario_vy, -JUMP_FORCE)

        # Exit
        with if_(act == 10):
            assign(cont, False)

        # Gravity
        assign(mario_vy, mario_vy + GRAVITY * dt)
        assign(mario_y, mario_y + mario_vy * dt)

        # Collision with ground
        # If Mario is below GROUND_LEVEL, clamp him
        with if_(mario_y > GROUND_LEVEL):
            assign(mario_y, GROUND_LEVEL)
            assign(mario_vy, 0)

        # Drawing
        # Optional marker pulse for scope trigger
        play("marker_pulse", "draw_marker_element")

        # Draw ground (centered at x=0, y=0 => so it's our "floor")
        draw_ground(0, 0)
        align()

        # Draw Mario
        draw_mario(mario_x, mario_y)
        align()

        # Wait for the frame to display
        wait(int(WAIT_TIME))
        assign(t, t + TIME_STEP_SIZE)

# =============================================================================
# 5. Running & Keyboard Input
# =============================================================================
if __name__ == "__main__":
    job = qm.execute(mario_game)
    print("Mario game started (no border, no enemies, with ground collision).")

    # For demonstration, we read keystrokes and set IO lines accordingly.
    # In your actual setup, you might wire a real controller or something else.
    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                # Quit
                qm.set_io2_value(10)
                break
            elif event.key == keyboard.KeyCode.from_char('a'):
                # Left
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io1_value(1)
                else:
                    qm.set_io1_value(0)
            elif event.key == keyboard.KeyCode.from_char('d'):
                # Right
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io1_value(2)
                else:
                    qm.set_io1_value(0)
            elif event.key == keyboard.KeyCode.from_char('w'):
                # Jump
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io2_value(5)
                else:
                    qm.set_io2_value(0)
            else:
                pass

    print("Game ended!")
