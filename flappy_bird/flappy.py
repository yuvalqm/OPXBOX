import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *

from sprites import *

# %%

# TODO implement some smaller programs for testing.
# TODO fix the units of the measurement

debug = False

# the size of the field
# The objects on the field wion 0ll be able to move in the range of +-1*field_size.
field_size = 0.3  # V

# The upper limit of the number of rays that are processed
N_rays = 10  # 1

# the speed with which the rays move
v_ray = 1.5  # V/s

# the duration before the rays decay
max_ray_age = 2  # s

# the delay between spawning rays. I.e. spawns at most 1 ray in that duration
ray_spawn_delay = 0.1  # s

# Number of pillars to be spawned
N_pillars = 1  # 1

# radius of the pillars
R_pillar = field_size * 0.075  # V

# speed with which the pillars move
v_pillar = 0.2  # V/s

# acceleration the bird experiences then the play presses the forward button
bird_acceleration = 0.5 * 2  # (2*)V/s^2

# Max speed of the bird
max_speed = 1  # V/s

# the rotational speed of the bird
bird_rotation_speed = 2.0  # 2*pi/s

# the amount of time the game is advanced every tick
# as the timing is not implemented yet, this value sets the amount of time that passes for each tick.
# and thus is used for the dt in the equations moving the elements.
time_step_size = 0.01  # s

# the duration of the pulse used to probe the user input (for one side of the controller)
user_input_pulse_length = 500000  # ns

# intermediate_frequency that is used for all components
intermediate_frequency = 0

# the pulse length in number of samples used to draw the sprites
sprite_length = 100

# The time to wait after drawing all sprites before starting processing the next frame. This is independent of `time_step_size`.
wait_time = 1e7 / 2  # ns

# the amplitude used to probe the controller.
input_probe_voltage = .5  # V

# Define additional game parameters
gravity = 0.1  # Adjust gravity to control the bird's fall speed
flap_force = -0.1  # Adjust flap_force to control the bird's jump height
pillar_speed = 0.5  # Adjust pillar_speed to control the pillar's horizontal speed
pillar_interval = 2.0  # Adjust pillar_interval to control the time between pillar spawns
bird_y_max = field_size - 0.1  # Define the maximum height for the bird

# %%

configuration = {
    'version': 1,
    'controllers': {
        'con1': {
            'type': 'opx1',
            'analog_outputs': {
                1: {'offset': +0.0},
                2: {'offset': +0.0},
                3: {'offset': +0.0},
                4: {'offset': +0.0},
            },
            'digital_outputs': {
                1: {},
            },
            'analog_inputs': {
                1: {'offset': -0.0},
                2: {'offset': -0.0},
            }
        }
    },
    'elements': {
        'screen': {
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 3),
            },
            'intermediate_frequency': intermediate_frequency,
            'digitalInputs': {
                'draw_marker': {
                    'port': ('con1', 1),
                    'delay': 0,
                    'buffer': 0,
                },
            },
            'operations': {
                "bird": "bird",
                "pillar": "pillar",
                "border": "border",
                "opillar": "opillar"
            },
        },
        'draw_marker_element': {
            'singleInput': {
                'port': ('con1', 3),
            },
            'intermediate_frequency': intermediate_frequency,
            'operations': {
                "marker_pulse": "marker_pulse",
            },
        },
        'user_input_element': {
            'singleInput': {
                'port': ('con1', 4),
            },
            'outputs': {
                'a': ('con1', 1),
                'b': ('con1', 2),
            },
            'intermediate_frequency': intermediate_frequency,
            'operations': {
                "measure_user_input": "measure_user_input",
            },
            'time_of_flight': 100,
            'smearing': 0
        },
    },
    'pulses': {
        **{n: {
            'operation': 'control',
            'length': sprite_length,
            'waveforms': {k: f"{n}_{l}" for k, l in zip(["I", "Q"], ["x", "y"])},
        }
            for n in ["bird", "pillar", "border", "opillar"]},
        "measure_user_input": {
            "operation": "measurement",
            'length': user_input_pulse_length,
            "integration_weights": {
                "constant": "cosine_weights",
            },
            'waveforms': {"single": "input_wf"},
        },
        "marker_pulse": {
            "operation": "control",
            'length': sprite_length,
            'waveforms': {"single": "marker_wf"},
        }
    },
    'waveforms': {
        **{
            f"bird_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_bird_pulse(sprite_length) * field_size * 0.1)
        },
        **{
            f"pillar_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_pillar_pulse(sprite_length, 1) * R_pillar*2)
        },
        **{
            f"border_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_border_pulse(sprite_length) * field_size)
        },
        **{
            f"opillar_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_reverse_pillar_pulse(sprite_length) * R_pillar*2)
        },
        # 'marker_wf': {'type':'arbitrary', 'samples':[.1]*50+[0]*50},
        'marker_wf': {"type": "constant", "sample": 0.2},
        'input_wf': {"type": "constant", "sample": input_probe_voltage},
    },
    'digital_waveforms': {
        'draw_trigger': {
            'samples': [(1, 0)]
        }
    },
    "integration_weights": {
        "cosine_weights": {
            "cosine": [(1.0, user_input_pulse_length)],
            "sine": [(0.0, user_input_pulse_length)],
        },
        "sine_weights": {
            "cosine": [(0.0, user_input_pulse_length)],
            "sine": [(1.0, user_input_pulse_length)],
        },
    },
}

# %%

qop_ip = '192.168.116.171'
qmm = QuantumMachinesManager(host=qop_ip, port = 80)

# %%

qm = qmm.open_qm(configuration)


# %%

def move_cursor(x, y):
    # go to the (x, y) position
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)


def get_rot_amp(a):
    return amp(Math.cos2pi(a), -Math.sin2pi(a), Math.sin2pi(a), Math.cos2pi(a))


def draw_by_name(name, x, y, a):
    move_cursor(x, y)
    play(name * get_rot_amp(a), 'screen')
    align()


def draw_bird(x, y, a):
    move_cursor(x, y)
    play('bird' * get_rot_amp(a), 'screen')
    align()

def draw_bird(x, y, a):
    move_cursor(x, y)
    play('bird' * get_rot_amp(a), 'screen')
    align()

def draw_pillar(x, y, a):
    move_cursor(x, y)
    play('bird' * get_rot_amp(a), 'screen')
    align()

def draw_ray(x, y, a):
    move_cursor(x, y)
    play('ray' * get_rot_amp(a), 'screen')
    align()


def draw_pillar(x, y):
    move_cursor(x, y)
    play('pillar', 'screen')
    align()

def draw_reverse_pillar(x, y):
    move_cursor(x, y)
    play('opillar', 'screen')
    align()


def draw_border():
    move_cursor(0, 0)
    play('border', 'screen')
    align()


def get_distance(ax, ay, bx, by):
    distance = declare(fixed)
    distance = Math.sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by))
    return distance


def ray_hit(ray_x, ray_y, pillar_x, pillar_y):
    hit = declare(bool, False)

    distance = get_distance(ray_x, ray_y, pillar_x, pillar_y)

    with if_(distance < R_pillar):
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
        cycle_clip(e, field_size, -field_size)
    return x, y


def clip_angle(a):
    return cycle_clip(a, .5, -.5)


def clip_velocity(v):
    return clip(v, max_speed, -max_speed)


def get_inputs(move, act):
    """
    The inputs
    IO1
    w - forward
    a - left
    d - right

    IO2
    space - fire
    escape - end game
    """

    assign(move, IO1)
    assign(act, IO2)
    if debug:
        save(move, a_stream)
        save(act, b_stream)

    return move, act


# %%

rng = np.random.default_rng(seed=1234)
# %%

with program() as game:
    bird_a = declare(fixed, 0)
    bird_x = declare(fixed, 0)
    bird_y = declare(fixed, 0)
    bird_vx = declare(fixed, 0)
    bird_vy = declare(fixed, 0)

    pillars_active = declare(bool, value=[True] * N_pillars)
    pillars_x = declare(fixed, value=rng.uniform(-field_size, field_size, N_pillars))
    pillars_y = declare(fixed, value=rng.uniform(0, 0, N_pillars))
    pillars_a = declare(fixed, value=rng.uniform(-.5, .5, N_pillars))

    # Add variables to keep track of game state
    bird_flap = declare(int, 0)  # Variable to track if the player flaps
    pillar_x = declare(fixed, field_size)  # Initial horizontal position of the pillars
    pillar_y = declare(fixed, 0)  # Vertical position of the pillars
    pillar_gap = 0.1  # Adjust pillar_gap to control the gap between pillars
    score = declare(int, 0)  # Player's score
    game_over = declare(bool, False)  # Flag to indicate game over

    t = declare(fixed, 0)
    t_prim = declare(fixed, 0)
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

    if debug:
        a_stream = declare_stream()
        b_stream = declare_stream()

    # Game loop
    # with while_(t < 500*time_step_size):
    with while_(cont):
        assign(dt, t - t_prim)
        assign(t_prim, t)

        # process user inputs
        assign(ui_phi, 0)  # The angle update that the user inputted
        assign(ui_forward, 0)  # The forward acceleration that is inputted
        assign(ui_fire, False)  # The forward acceleration that is inputted
        assign(move, 0)  # The user input
        assign(act, 0)  # The user input



        '''
        The inputs
        w - forward
        a - left
        d - right
        
        space - fire
        escape - end game
        '''

        get_inputs(move, act)
        with if_(act == 5):
            assign(bird_flap, 1)

        # # update the velocity and position
        assign(bird_vy, bird_vy - gravity * dt)
        assign(bird_y, bird_y + bird_vy * dt)

        # Handle bird flapping
        with if_(bird_flap == 1):
            assign(bird_vy, -flap_force)
            assign(bird_flap, 0)

        # Spawn pillars
        #     def for_(var= N_pillars, init= 1, cond= N_pillars<=11, update= N_pillars + 1):
        #     for pill in range(1, 11, 1):
        #         # with if_(t - t_last_pillar_spawn >= pillar_interval):
        #         #     assign(t_last_pillar_spawn, t)
        #         assign(pillar_x, rng.uniform(-field_size + pillar_gap, field_size - pillar_gap))

        # Move pillars
        assign(pillar_x, pillar_x - pillar_speed * dt)

        # Check for collisions
        # with if_(bird_y > bird_y_max or bird_y < -bird_y_max):
        #     assign(game_over, True)
        #
        # with if_(bird_x < pillar_x + R_pillar & bird_x > pillar_x - R_pillar):
        #     with if_(bird_y > pillar_y + pillar_gap / 2 or bird_y < pillar_y - pillar_gap / 2):
        #         assign(game_over, True)

        # Update score
        with if_(bird_x > pillar_x):
            assign(score, score + 1)

        # process crashes
        with for_(j, 0, j < N_pillars, j + 1):
            with if_(pillars_active[j]):
                # with if_(ray_hit(rays_x[i], rays_y[i], pillars_x[j], pillars_y[j])):
                with if_((get_distance(bird_x, bird_y, pillars_x[j], pillars_y[j]) < R_pillar)):
                    assign(crashed, True)


        process border collisions
        process_border_collisions(bird_x, bird_y)
        with for_(i, 0, i < N_pillars, i + 1):
            with if_(pillars_active[i]):
                process_border_collisions(pillars_x[i], pillars_y[i])

        # draw graphics
        play("marker_pulse", "draw_marker_element")
        draw_bird(bird_x, bird_y, bird_a)
        draw_pillar(pillar_x, pillar_y)
        draw_reverse_pillar(pillar_x, -pillar_y * 2)
        draw_pillar(pillar_x + pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 2*pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 2*pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 3 * pillar_gap, pillar_y * 3)
        draw_reverse_pillar(pillar_x + 3 * pillar_gap, -pillar_y * 6)
        draw_pillar(pillar_x + 4 * pillar_gap, pillar_y * 4)
        draw_reverse_pillar(pillar_x + 4 * pillar_gap, -pillar_y * 8)
        draw_pillar(pillar_x + 4 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 4 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 5 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 5 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 6 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 6 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 7 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 7 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 8 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 8 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 9 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 9 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 10 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 10 * pillar_gap, -pillar_y * 2)
        draw_pillar(pillar_x + 11 * pillar_gap, pillar_y)
        draw_reverse_pillar(pillar_x + 11 * pillar_gap, -pillar_y * 2)
        draw_border()

        # wait until everything is drawn
        align()

        wait(int(wait_time))

        # update time
        assign(t, t + time_step_size)

    if debug:
        with stream_processing():
            a_stream.save_all('move')
            b_stream.save_all('act')

# %%


def send_over_io(io_num, value, set_value):
    if not set_value:
        value = 0
    if io_num == 1:
        qm.set_io1_value(value)
    elif io_num == 2:
        qm.set_io2_value(value)


if __name__ == '__main__':
    job = qm.execute(game)
    res = job.result_handles

    print('Game is on!')
    with keyboard.Events() as events:
        for event in events:
            # nothing: 0
            # w: 1
            # s: 2
            # a: 3
            # d: 4
            # space: 5
            # left crtl: 6
            # escape: 10

            if event.key == keyboard.Key.esc:
                send_over_io(2, 10, type(event) is events.Press)
                break
            elif event.key == keyboard.Key.space:
                send_over_io(2, 5, type(event) is events.Press)
            elif event.key == keyboard.Key.ctrl_l:
                send_over_io(2, 6, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('w'):
                send_over_io(1, 1, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('s'):
                send_over_io(1, 2, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('a'):
                send_over_io(1, 3, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('d'):
                send_over_io(1, 4, type(event) is events.Press)
            else:
                pass

    if debug:
        res.wait_for_all_values()
        move = res.move.fetch_all()
        act = res.act.fetch_all()
        plt.plot(move)
        plt.plot(act)
        plt.show()
        # print(move)
        # print(act)
