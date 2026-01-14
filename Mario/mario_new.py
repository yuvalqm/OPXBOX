import numpy as np
import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *
from sprites_mario import *
import random
import time

# =============================================================================
# Configuration Parameters
# =============================================================================
DEBUG = True
CONTROLLER = False

# Field and object parameters
FIELD_SIZE = 0.3           # V, size of the field
N_OBSTACLES = 5            # Number of obstacles (goombas/pipes)
OBSTACLE_WIDTH = 0.08      # V, width of obstacles
V_OBSTACLE = 0.15          # V/s, speed of obstacles moving left

# Mario parameters
MAX_SPEED = 0.3            # V/s, maximum Mario speed
MARIO_WIDTH = 0.06         # V, Mario's width
MARIO_HEIGHT = 0.08        # V, Mario's height

# Timing parameters
TIME_STEP_SIZE = 0.01      # s, time advanced per tick
USER_INPUT_PULSE_LENGTH = 500000  # ns, pulse length for user input probing
SPRITE_LENGTH = 16500      # number of samples used to draw sprites
WAIT_TIME = 1e7 / 2        # ns, wait time after drawing sprites

# Controller input parameters
INPUT_PROBE_VOLTAGE = 0.5  # V, amplitude used to probe the controller

# Additional game parameters
GRAVITY = 0.4              # Gravity affecting Mario's fall speed
JUMP_FORCE = 0.25          # Force applied when Mario jumps
GROUND_Y = -FIELD_SIZE + 0.05  # Y position of the ground
MARIO_X = -FIELD_SIZE / 2  # Mario stays at this X position

# =============================================================================
# QUA Configuration Dictionary
# =============================================================================
configuration = {
    'version': 1,
    'controllers': {
        'con1': {
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
                },
            },
        },
    },
    'elements': {
        'screen': {
            'mixInputs': {
                'I': ('con1', 5, 5),
                'Q': ('con1', 5, 6),
            },
            'intermediate_frequency': 0,
            'digitalInputs': {
                'draw_marker': {
                    'port': ('con1', 5, 1),
                    'delay': 0,
                    'buffer': 0,
                },
            },
            'operations': {
                "mario": "mario",
                "goomba": "goomba",
                "pipe": "pipe",
                "block": "block",
                "coin": "coin",
                "border": "border",
                "blank": "blank",
                "game_over": "game_over",
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
        'user_input_element': {
            'singleInput': {
                'port': ('con1', 5, 2),
            },
            'outputs': {
                'out2': ('con1', 5, 2),
            },
            'intermediate_frequency': 0,
            'operations': {
                "measure_user_input": "measure_user_input",
            },
            'time_of_flight': 136,
            'smearing': 0
        },
    },
    'pulses': {
        **{n: {
            'operation': 'control',
            'length': SPRITE_LENGTH,
            'waveforms': {k: f"{n}_{l}" for k, l in zip(["I", "Q"], ["x", "y"])},
        } for n in [
            "mario", "goomba", "pipe", "block", "coin", "border", "game_over"
        ]},
        "measure_user_input": {
            "operation": "measurement",
            'length': USER_INPUT_PULSE_LENGTH,
            "integration_weights": {"cos": "cosine_weights"},
            'waveforms': {"single": "input_wf"},
        },
        "marker_pulse": {
            "operation": "control",
            'length': SPRITE_LENGTH,
            'waveforms': {"single": "marker_wf"},
        },
        "blank": {
            "operation": "control",
            "length": 16,
            "waveforms": {
                "I":"blank_wf",
                "Q":"blank_wf",
            }
        },
    },
    'waveforms': {
        **{
            f"mario_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_mario_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.15)
        },
        **{
            f"goomba_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_goomba_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.12)
        },
        **{
            f"pipe_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pipe_pulse(SPRITE_LENGTH, 2) * FIELD_SIZE * 0.15)
        },
        **{
            f"block_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_block_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.08)
        },
        **{
            f"coin_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_coin_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.05)
        },
        **{
            f"border_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_border_pulse(SPRITE_LENGTH) * FIELD_SIZE)
        },
        **{
            f"game_over_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], 
                            get_game_over_text(SPRITE_LENGTH) * FIELD_SIZE * 0.08)
        },
        'marker_wf': {"type": "constant", "sample": 0.2},
        'input_wf': {"type": "constant", "sample": INPUT_PROBE_VOLTAGE},
        "blank_wf": {"type": "constant", "sample": 0.0},
    },
    'digital_waveforms': {
        'draw_trigger': {'samples': [(1, 0)]}
    },
    "integration_weights": {
        "cosine_weights": {
            "cosine": [(1.0, USER_INPUT_PULSE_LENGTH)],
            "sine": [(0.0, USER_INPUT_PULSE_LENGTH)],
        },
        "sine_weights": {
            "cosine": [(0.0, USER_INPUT_PULSE_LENGTH)],
            "sine": [(1.0, USER_INPUT_PULSE_LENGTH)],
        },
    },
}

# =============================================================================
# QUA Machine Setup
# =============================================================================
qop_ip = '172.16.33.107'
qmm = QuantumMachinesManager(host=qop_ip, port=9510)
qm = qmm.open_qm(configuration)

# =============================================================================
# Graphics and Utility Functions
# =============================================================================
def move_cursor(x, y):
    """Set the cursor position on the screen."""
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)

def get_rot_amp(a):
    """Calculate the rotation amplitude based on angle a."""
    return amp(Math.cos2pi(a), -Math.sin2pi(a),
               Math.sin2pi(a), Math.cos2pi(a))

def draw_by_name(name, x, y, a=0):
    move_cursor(x, y)
    play(name * get_rot_amp(a), 'screen')
    align()

def draw_mario(x, y):
    move_cursor(x, y)
    play('mario', 'screen')
    align()

def draw_goomba(x, y):
    move_cursor(x, y)
    play('goomba', 'screen')
    align()

def draw_pipe(x, y):
    move_cursor(x, y)
    play('pipe', 'screen')
    align()

def draw_block(x, y):
    move_cursor(x, y)
    play('block', 'screen')
    align()

def draw_border():
    move_cursor(0, 0)
    play('border', 'screen')
    align()

def draw_game_over(x, y):
    move_cursor(x, y)
    play('game_over', 'screen')
    align()

def get_distance(ax, ay, bx, by):
    distance = declare(fixed)
    distance = Math.sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by))
    return distance

def cycle_clip(x, upper, lower):
    with if_(x > upper):
        assign(x, lower)
    with elif_(x < lower):
        assign(x, upper)
    return x

def clip(x, upper, lower):
    with if_(x > upper):
        assign(x, upper)
    with elif_(x < lower):
        assign(x, lower)
    return x

def get_inputs(move, act):
    """
    Retrieve user inputs.
    
    IO1: Not used (Mario doesn't move horizontally)
    IO2: space - jump (5), escape - end game (10)
    """
    assign(move, IO1)
    assign(act, IO2)
    if DEBUG:
        save(move, a_stream)
        save(act, b_stream)
    return move, act

# =============================================================================
# Game Program
# =============================================================================
rng = np.random.default_rng(seed=1234)

with program() as mario_game:
    # Declare game variables
    mario_x = declare(fixed, MARIO_X)
    mario_y = declare(fixed, GROUND_Y + MARIO_HEIGHT)
    mario_vy = declare(fixed, 0)
    on_ground = declare(bool, True)

    # Obstacles (goombas and pipes)
    obstacles_active = declare(bool, value=[True] * N_OBSTACLES)
    obstacles_x = declare(fixed, value=np.linspace(FIELD_SIZE, FIELD_SIZE * 2, 
                                                     num=N_OBSTACLES).tolist())
    obstacles_y = declare(fixed, value=[GROUND_Y + 0.04] * N_OBSTACLES)
    obstacles_type = declare(int, value=[i % 2 for i in range(N_OBSTACLES)])  # 0=goomba, 1=pipe

    # Game state variables
    jump_pressed = declare(bool, False)
    score = declare(int, 0)
    game_over = declare(bool, False)

    t = declare(fixed, 0)
    t_prev = declare(fixed, 0)
    dt = declare(fixed, 0)
    i = declare(int, 0)
    j = declare(int, 0)

    move = declare(int)
    act = declare(int)

    cont = declare(bool, True)
    crashed = declare(bool, False)

    if DEBUG:
        a_stream = declare_stream()
        b_stream = declare_stream()

    # Main game loop
    with while_(cont):
        assign(dt, t - t_prev)
        assign(t_prev, t)

        # Process user inputs
        assign(jump_pressed, False)
        assign(move, 0)
        assign(act, 0)
        get_inputs(move, act)
        
        with if_(act == 5):
            with if_(on_ground):
                assign(jump_pressed, True)
        
        with if_(act == 10):
            assign(cont, False)

        # Update Mario physics
        with if_(jump_pressed):
            assign(mario_vy, JUMP_FORCE)
            assign(on_ground, False)
        
        # Apply gravity
        with if_(~on_ground):
            assign(mario_vy, mario_vy - GRAVITY * dt)
        
        assign(mario_y, mario_y + mario_vy * dt)
        
        # Ground collision
        with if_(mario_y <= GROUND_Y + MARIO_HEIGHT):
            assign(mario_y, GROUND_Y + MARIO_HEIGHT)
            assign(mario_vy, 0)
            assign(on_ground, True)

        # Move obstacles left
        with for_(i, 0, i < N_OBSTACLES, i + 1):
            assign(obstacles_x[i], obstacles_x[i] - V_OBSTACLE * dt)
            
            # Respawn obstacles that went off screen
            with if_(obstacles_x[i] < -FIELD_SIZE):
                assign(obstacles_x[i], FIELD_SIZE + Random().rand_fixed() * 0.2)
                assign(obstacles_y[i], GROUND_Y + 0.04)
                assign(score, score + 1)

        # Check collisions
        with if_(~crashed):
            with for_(j, 0, j < N_OBSTACLES, j + 1):
                with if_(obstacles_active[j]):
                    # Simple bounding box collision
                    collision_detected = declare(bool, False)
                    
                    with if_((Math.abs(mario_x - obstacles_x[j]) < OBSTACLE_WIDTH + MARIO_WIDTH)):
                        with if_((Math.abs(mario_y - obstacles_y[j]) < MARIO_HEIGHT + 0.06)):
                            assign(crashed, True)

        # Draw graphics
        play("marker_pulse", "draw_marker_element")
        
        with if_(crashed):
            draw_game_over(-0.2, 0)
        with else_():
            play("blank", "screen")
            
            # Draw ground line (simple)
            # draw_border()
            
            # Draw obstacles
            with for_(i, 0, i < N_OBSTACLES, i + 1):
                with if_(obstacles_x[i] < FIELD_SIZE):
                    with if_(obstacles_type[i] == 0):
                        draw_goomba(obstacles_x[i], obstacles_y[i])
                    with else_():
                        draw_pipe(obstacles_x[i], obstacles_y[i])

            # Draw Mario last so he appears on top
            draw_mario(mario_x, mario_y)
        
        align()
        wait(int(WAIT_TIME))   
        assign(t, t + TIME_STEP_SIZE)

    if DEBUG:
        with stream_processing():
            a_stream.save_all('move')
            b_stream.save_all('act')

# =============================================================================
# IO and Main Execution
# =============================================================================
def send_over_io(io_num, value, set_value):
    if not set_value:
        value = 0
    if io_num == 1:
        qm.set_io1_value(value)
    elif io_num == 2:
        qm.set_io2_value(value)

if __name__ == '__main__':
    print("=" * 60)
    print("SUPER MARIO OPXBOX GAME")
    print("=" * 60)
    print("Controls:")
    print("  SPACE - Jump")
    print("  ESC   - Quit")
    print("")
    print("Avoid the Goombas and Pipes!")
    print("=" * 60)
    
    job = qm.execute(mario_game)
    res = job.result_handles
    
    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                send_over_io(2, 10, type(event) is events.Press)
                break
            elif event.key == keyboard.Key.space:
                send_over_io(2, 5, type(event) is events.Press)
    
    print("\nGame Over! Thanks for playing!")
