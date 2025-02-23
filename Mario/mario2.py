import numpy as np

def resample_trace(x, y, points=100):
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def get_mario_shape(points=100, radius=0.4):
    """Simple circle for 'Mario'."""
    t = np.linspace(0, 2*np.pi, 12)
    x = radius * np.cos(t)
    y = radius * np.sin(t)
    return resample_trace(x, y, points)

def shifted_waveform(x_shift, y_shift, shape, scale=0.3):
    """
    Return a (x_vals, y_vals) shape that's shifted by (x_shift, y_shift).
    'shape' is (2, points) from get_mario_shape.
    'scale' is an overall scale factor for the entire shape.
    """
    x_vals = shape[0] * scale + x_shift
    y_vals = shape[1] * scale + y_shift
    return x_vals, y_vals

X_POSITIONS = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
Y_POSITIONS = [-0.5, -0.3]  # just two for demonstration

def build_mario_waveforms():
    """Return a dict of waveform entries for each (x, y) in X_POSITIONS, Y_POSITIONS."""
    base_shape = get_mario_shape(points=100, radius=0.4)
    waveforms = {}
    pulses = {}
    
    for x_shift in X_POSITIONS:
        for y_shift in Y_POSITIONS:
            name = f"mario_x_{x_shift:+.2f}__y_{y_shift:+.2f}"
            x_vals, y_vals = shifted_waveform(x_shift, y_shift, base_shape, scale=0.3)
            
            # Create waveform dict entries
            waveforms[f"{name}_x"] = {
                "type": "arbitrary",
                "samples": x_vals.tolist()
            }
            waveforms[f"{name}_y"] = {
                "type": "arbitrary",
                "samples": y_vals.tolist()
            }
            
            # Create a pulse entry that references these waveforms
            pulses[name] = {
                "operation": "control",
                "length": 100,
                "waveforms": {
                    "I": f"{name}_x",
                    "Q": f"{name}_y"
                }
            }
    
    return waveforms, pulses

mario_waveforms, mario_pulses = build_mario_waveforms()

configuration = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1000",
            "fems": {
                5: {
                    "type": "LF",
                    "analog_outputs": {i: {"offset": 0.0} for i in range(1, 9)},
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
                # We'll fill these dynamically from mario_pulses
            },
        },
    },
    "pulses": {
        # We'll fill from mario_pulses
    },
    "waveforms": {
        # We'll fill from mario_waveforms
    },
}
# Insert them
configuration["pulses"].update(mario_pulses)
configuration["waveforms"].update(mario_waveforms)

# Add a single "marker_pulse" if you want
configuration["pulses"]["marker_pulse"] = {
    "operation": "control",
    "length": 16,
    "waveforms": {"single": "marker_wf"},
}
configuration["waveforms"]["marker_wf"] = {
    "type": "constant",
    "sample": 0.2
}
configuration["elements"]["screen"]["operations"].update({
    name: name for name in mario_pulses
})
configuration["elements"]["screen"]["operations"]["marker_pulse"] = "marker_pulse"

from qm import QuantumMachinesManager
from qm.qua import *
from pynput import keyboard
import math

qmm = QuantumMachinesManager("172.16.33.107",9510)
qm = qmm.open_qm(configuration)

# Utility to pick nearest discrete offset
def nearest_offset(val, allowed):
    # returns the item in 'allowed' that is closest to 'val'
    # we can't do Python logic inside QUA, so we'll do it in Python after reading from QUA or by a known approach.
    # In real QUA, you might have to do a series of if_ checks to clamp or pick a discrete index.
    return min(allowed, key=lambda x: abs(x - val))

def draw_mario_at(x, y):
    """
    Picks the closest discrete waveforms for (x,y) and plays them.
    We'll do the nearest rounding in Python for demonstration.
    """
    # Round to nearest discrete
    x_rounded = nearest_offset(x, X_POSITIONS)
    y_rounded = nearest_offset(y, Y_POSITIONS)
    name = f"mario_x_{x_rounded:+.2f}__y_{y_rounded:+.2f}"
    play(name, "screen")

TIME_STEP_SIZE = 0.01
WAIT_TIME = 2e6
GRAVITY = 0.05
JUMP_FORCE = 0.3
MARIO_SPEED = 0.15
GROUND_LEVEL = -0.1  # just pick a ground

with program() as discrete_mario_game:
    mario_x = declare(fixed, value=0)
    mario_y = declare(fixed, value=-0.2)
    mario_vy = declare(fixed, value=0)

    t = declare(fixed, value=0)
    t_prev = declare(fixed, value=0)
    dt = declare(fixed, value=0)

    move = declare(int, value=0)
    act = declare(int, value=0)
    cont = declare(bool, value=True)

    with while_(cont):
        assign(dt, t - t_prev)
        assign(t_prev, t)

        # Simple input logic:
        assign(move, IO1)  # 1 => left, 2 => right
        assign(act, IO2)   # 5 => jump, 10 => exit

        # Move horizontally
        with if_(move == 1):
            assign(mario_x, mario_x - MARIO_SPEED * dt)
        with if_(move == 2):
            assign(mario_x, mario_x + MARIO_SPEED * dt)

        # Jump
        with if_(act == 5):
            # jump up
            assign(mario_vy, +JUMP_FORCE)
        # Exit
        with if_(act == 10):
            assign(cont, False)

        # Gravity
        assign(mario_vy, mario_vy - GRAVITY * dt)
        assign(mario_y, mario_y + mario_vy * dt)

        # Ground collision
        with if_(mario_y < GROUND_LEVEL):
            assign(mario_y, GROUND_LEVEL)
            assign(mario_vy, 0)

        # Optional scope marker
        play("marker_pulse", "screen")

        # Now we "draw" Mario by picking the closest waveforms
        # But we can't do that nearest offset logic in QUA directly.
        # So we do a trick: store the position in a QUA variable, read it in Python, and do a "play" from Python.
        # However, that means the entire code must run on the CPU side, not purely in QUA.
        # 
        # Instead, we do a big if-else chain in QUA. For a small grid, it's possible:
        # e.g. with if_(mario_x < -0.25): with if_(mario_y < -0.4): play("mario_x_-0.30__y_-0.50") ...
        # 
        # For demonstration, let's do a big chain:

        # We'll define a few rung-based checks for x, y
        with if_(mario_x < -0.25):
            with if_(mario_y < -0.4):
                play("mario_x_-0.30__y_-0.50", "screen")
            with elif_(mario_y < -0.35):
                play("mario_x_-0.30__y_-0.30", "screen")
            # ... and so on
        with elif_(mario_x < -0.15):
            with if_(mario_y < -0.4):
                play("mario_x_-0.20__y_-0.50", "screen")
            with elif_(mario_y < -0.35):
                play("mario_x_-0.20__y_-0.30", "screen")
            # ...
        # etc. for all discrete combos
        # This is tedious, but that's the only pure-QUA approach.

        # We'll do a minimal version just to illustrate:
        align()

        wait(int(WAIT_TIME))
        assign(t, t + TIME_STEP_SIZE)

# Running from Python
if __name__ == "__main__":
    job = qm.execute(discrete_mario_game)
    print("Discrete Mario game started.")

    from pynput import keyboard
    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                qm.set_io2_value(10)
                break
            elif event.key == keyboard.KeyCode.from_char('a'):
                # left
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io1_value(1)
                else:
                    qm.set_io1_value(0)
            elif event.key == keyboard.KeyCode.from_char('d'):
                # right
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io1_value(2)
                else:
                    qm.set_io1_value(0)
            elif event.key == keyboard.KeyCode.from_char('w'):
                # jump
                if isinstance(event, keyboard.Events.Press):
                    qm.set_io2_value(5)
                else:
                    qm.set_io2_value(0)
            else:
                pass

    print("Game ended.")
