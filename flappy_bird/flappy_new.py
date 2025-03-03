import numpy as np
import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *
from sprites_new import *
import random
import time

# =============================================================================
# Configuration Parameters
# =============================================================================
DEBUG = True
CONTROLLER = True

# Field and object parameters
FIELD_SIZE = 0.3           # V, size of the field
N_PILLARS = 7                  # Number of pillars to be spawned
R_PILLAR = FIELD_SIZE * 0.075  # V, radius of the pillars
V_PILLAR = 0.02             # V/s, speed of the pillars

# Bird parameters
MAX_SPEED = 0.2              # V/s, maximum bird speed


# Timing parameters
TIME_STEP_SIZE = 0.01      # s, time advanced per tick
USER_INPUT_PULSE_LENGTH = 500000  # ns, pulse length for user input probing
SPRITE_LENGTH = 16500        # number of samples used to draw sprites
WAIT_TIME = 1e7 / 2        # ns, wait time after drawing sprites

# Controller input parameters
INPUT_PROBE_VOLTAGE = 0.5  # V, amplitude used to probe the controller

# Additional game parameters
GRAVITY = 0.3         # Gravity affecting the bird's fall speed
FLAP_FORCE = -0.2     # Force applied when the bird flaps (controls jump height)
PILLAR_SPEED = 0.3    # Horizontal speed of pillars
PILLAR_INTERVAL = 5.0 # Time between pillar spawns
BIRD_Y_MAX = FIELD_SIZE - 0.1  # Maximum height for the bird

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
                3: {
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
                "bird": "bird",
                "pillar_short": "pillar_short",
                "pillar_medium": "pillar_medium",
                "pillar_long": "pillar_long",
                "border": "border",
                "r_pillar_short": "r_pillar_short",
                "r_pillar_medium": "r_pillar_medium",
                "r_pillar_long": "r_pillar_long",
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
            "bird", "pillar_short", "pillar_medium", "pillar_long",
            "border", "r_pillar_short", "r_pillar_medium", "r_pillar_long","game_over"
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
            f"bird_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_bird_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.1)
        },
        **{
            f"pillar_short_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pillar_pulse(SPRITE_LENGTH, 2) * R_PILLAR * 2)
        },
        **{
            f"pillar_medium_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pillar_pulse(SPRITE_LENGTH, 3) * R_PILLAR * 2)
        },
        **{
            f"pillar_long_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pillar_pulse(SPRITE_LENGTH, 4) * R_PILLAR * 2)
        },
        **{
            f"border_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_border_pulse(SPRITE_LENGTH) * FIELD_SIZE)
        },
        **{
            f"r_pillar_short_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pillar_pulse(SPRITE_LENGTH, 2, -1) * R_PILLAR * 2)
        },
        **{
            f"r_pillar_medium_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pillar_pulse(SPRITE_LENGTH, 3, -1) * R_PILLAR * 2)
        },
        **{
            f"r_pillar_long_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"],
                            get_pillar_pulse(SPRITE_LENGTH, 4, -1) * R_PILLAR * 2)
        },
        **{
            f"game_over_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_word_pulse(SPRITE_LENGTH, [g(), a(), m(), e1(), space(), o(), v(), e2(), r()]) * FIELD_SIZE * 0.1)
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

def draw_by_name(name, x, y, a):
    move_cursor(x, y)
    play(name * get_rot_amp(a), 'screen')
    align()

def draw_bird(x, y, a):
    move_cursor(x, y)
    play('bird' * get_rot_amp(a), 'screen')
    align()

def draw_ray(x, y, a):
    move_cursor(x, y)
    play('ray' * get_rot_amp(a), 'screen')
    align()

def draw_pillar(x, y, length):
    move_cursor(x, y)
    if length == 1:
        play('pillar_short', 'screen')
    elif length == 2:
        play('pillar_medium', 'screen')
    elif length == 3:
        play('pillar_long', 'screen')
    align()


def draw_reverse_pillar(x, y, length):
    move_cursor(x, y)
    if length == 1:
        play('r_pillar_short', 'screen')
    elif length == 2:
        play('r_pillar_medium', 'screen')
    elif length == 3:
        play('r_pillar_long', 'screen')
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

def ray_hit(ray_x, ray_y, pillar_x, pillar_y):
    hit = declare(bool, False)
    distance = get_distance(ray_x, ray_y, pillar_x, pillar_y)
    with if_(distance < R_PILLAR):
        assign(hit, True)
    return hit

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

def process_border_collisions(x, y):
    for e in [x, y]:
        cycle_clip(e, FIELD_SIZE, -FIELD_SIZE)
    return x, y

def clip_angle(a):
    return cycle_clip(a, 0.5, -0.5)

def clip_velocity(v):
    return clip(v, MAX_SPEED, -MAX_SPEED)

def get_inputs(move, act):
    """
    Retrieve user inputs.
    
    IO1: w - forward, a - left, d - right
    IO2: space - fire, escape - end game
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

with program() as game_keyboard:
    # Declare game variables
    bird_a = declare(fixed, 0)
    bird_x = declare(fixed, 0)
    bird_y = declare(fixed, 0)
    bird_vx = declare(fixed, 0)
    bird_vy = declare(fixed, 0)

    pillars_active = declare(bool, value=[True] * N_PILLARS)
    pillars_y = declare(fixed, value=[random.uniform(-FIELD_SIZE, -FIELD_SIZE) for _ in range(N_PILLARS)])
    pillars_x = declare(fixed, value=np.linspace(-FIELD_SIZE, FIELD_SIZE, num=N_PILLARS).tolist())
    pillars_a = declare(fixed, value=np.linspace(-0.2, 0.2, num=N_PILLARS).tolist())

    # Game state variables
    bird_flap = declare(int, 0)
    pillar_x = declare(fixed, FIELD_SIZE)
    pillar_y = declare(fixed, -0.2)
    pillar_gap = 0.1
    score = declare(int, 0)
    game_over = declare(bool, False)
    offsety = declare(fixed,0)

    t = declare(fixed, 0)
    t_prev = declare(fixed, 0)
    t_last_pillar_spawn = declare(fixed, -8)
    dt = declare(fixed, 0)
    i = declare(int, 0)
    j = declare(int, 0)

    move = declare(int)
    act = declare(int)
    ui_phi = declare(fixed, 0)
    ui_forward = declare(fixed, 0)
    ui_fire = declare(bool, False)

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
        assign(ui_phi, 0)
        assign(ui_forward, 0)
        assign(ui_fire, False)
        assign(move, 0)
        assign(act, 0)
        get_inputs(move, act)
        with if_(act == 5):
            assign(bird_flap, 1)

        # Update bird physics
        assign(bird_vy, bird_vy - GRAVITY * dt)
        assign(bird_y, bird_y + bird_vy * dt)
        with if_(bird_flap == 1):
            assign(bird_vy, -FLAP_FORCE)
            assign(bird_flap, 0)

        # Move pillars
        for i in range (N_PILLARS):
            with if_(Math.abs(pillars_x[i]) < FIELD_SIZE):
                assign(pillars_x[i], pillars_x[i] - PILLAR_SPEED * dt)
            with else_():
                # Pillar went off left edge, respawn it on the right
                # e.g., place it slightly beyond +FIELD_SIZE so it moves in
                assign(pillars_x[i], FIELD_SIZE-0.0001)  
                assign(pillars_y[i], -FIELD_SIZE + Random().rand_fixed() *0.1)

        # Check collisions between bird and pillars
        with for_(j, 0, j < N_PILLARS, j + 1):
            with if_(pillars_active[j]):
                with if_(((bird_y < (pillars_y[j] + 5*R_PILLAR)) | (bird_y > (- pillars_y[j] - 5*R_PILLAR)))):
                    with if_((bird_x-pillars_x[j] <  3*R_PILLAR)):
                        assign(crashed, True)


        # Draw graphics
        play("marker_pulse", "draw_marker_element")
        
        with if_(crashed):
            draw_game_over(-0.15,0)
        with else_():
            play("blank", "screen")
            # draw_border()
            for i in range(N_PILLARS):
                # Only draw pillars that are within the visible field.
                with if_(pillars_x[i] < FIELD_SIZE):
                    length = 3
                    draw_pillar(pillars_x[i], pillars_y[i], length)
                    draw_reverse_pillar(pillars_x[i], -(pillars_y[i] * 1.5), length)

            # Draw the bird last so it appears on top of everything
            draw_bird(bird_x, bird_y, bird_a)
        align()
        wait(int(WAIT_TIME))   
        assign(t, t + TIME_STEP_SIZE)

    if DEBUG:
        with stream_processing():
            a_stream.save_all('move')
            b_stream.save_all('act')

def get_controller_input(I, act):
    with if_((I > -3.03) & (I < -3.07)):
        assign(act[0], 1)
    with if_((I > -1.35) & (I < -1.389)):
        assign(act[1], 1)
    with if_((I > -0.05) & (I < 0.05)):
        assign(act[2], 1)
    with if_((I > -0.5) & (I < 0.4)):
        assign(act[3], 1)
    with if_((I > 0.3) & (I < 0.4)):
        assign(act[4], 1)
    with if_((I > 0.2) & (I < 0.29)):
        assign(act[5], 1)


with program() as controller_debug:
    I = declare(fixed)
    I_stream = declare_stream()
    act = declare(int, value = [0,0,0,0,0,0])
    act_stream = declare_stream()
    length_s = declare_stream()
    lens = declare(int,0)
    n=declare(int,0)
    with infinite_loop_():
        # for k in range(6):
        #     assign(act[k], 0)
        reset_if_phase("user_input_element")
        play("marker_pulse", "draw_marker_element")
        measure("measure_user_input", "user_input_element",None, demod.full("cos", I, "out2"))
        align()
        get_controller_input(I, act)
        align()
        with for_(n,0,n<6,n+1):
            save(act[n], act_stream)
        # save(I,I_stream)
    with stream_processing():
        # I_stream.save('I')
        act_stream.save_all('act')

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


    
    ######### Controller input ########
    # if CONTROLLER:
    #    job = qm.execute(game_controller) 
    #    res = job.result_handles
    #    print('Game is on!')


    ######### Keyboard input ##########
    # if CONTROLLER == False:
    #     job = qm.execute(game_keyboard)
    #     res = job.result_handles
        # with keyboard.Events() as events:
        #     for event in events:
        #         # Mapping keys to actions:
        #         # escape: end game (10), space: fire (5), ctrl_l: (6),
        #         # w: forward (1), s: (2), a: left (3), d: right (4)
        #         if event.key == keyboard.Key.esc:
        #             send_over_io(2, 10, type(event) is events.Press)
        #             break
        #         elif event.key == keyboard.Key.space:
        #             send_over_io(2, 5, type(event) is events.Press)
        #         elif event.key == keyboard.Key.ctrl_l:
        #             send_over_io(2, 6, type(event) is events.Press)
        #         elif event.key == keyboard.KeyCode.from_char('w'):
        #             send_over_io(1, 1, type(event) is events.Press)
        #         elif event.key == keyboard.KeyCode.from_char('s'):
        #             send_over_io(1, 2, type(event) is events.Press)
        #         elif event.key == keyboard.KeyCode.from_char('a'):
        #             send_over_io(1, 3, type(event) is events.Press)
        #         elif event.key == keyboard.KeyCode.from_char('d'):
        #             send_over_io(1, 4, type(event) is events.Press)
    
    if DEBUG:
        job = qm.execute(controller_debug)
        res = job.result_handles
        print("test_controller")
        res.act.wait_for_values(1)
        while res.is_processing():
            print(res.act.fetch_all())
            time.sleep(0.3)

        # controller keys -> measured I:
        # Nothing: 0.45 - 0.52
        # A: -3.03 - -3.07
        # B: -1.35 - -1.389
        # Down: -0.05 - 0.05
        # Up: -0.5 - -0.4
        # Left: 0.3 - 0.4
        # Right: 0.2 - 0.29

    

