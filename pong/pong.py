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
N_rays = 1  # 1

# the speed with which the rays move
  # V/s

# the duration before the rays decay
max_ray_age = 2  # s

# the delay between spawning rays. I.e. spawns at most 1 ray in that duration
ray_spawn_delay = 0.1  # s

# Number of asteroids to be spawned
N_asteroids = 2  # 1

# radius of the asteroids
R_asteroid = field_size * 0.125  # V

# speed with which the asteroids move
v_asteroid = 0.2  # V/s

# acceleration the ship experiences then the play presses the forward button
player_acceleration = 0.5 * 2  # (2*)V/s^2

# Max speed of the ship
max_speed = 1  # V/s

# the rotational speed of the ship
ship_rotation_speed = 2.0  # 2*pi/s

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
                "player": "player",
                "ray": "ray",
                "border": "border",
                "game_over": "game_over",
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
            for n in ["player", "ray", "border", "game_over"]},
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
            f"player_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_pong_player_pulse(sprite_length) * field_size * 0.15)
        },
        **{
            f"ray_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_ray_pulse(sprite_length) * field_size * 0.005)
        },
        **{
            f"border_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_border_pulse(sprite_length) * field_size)
        },
        **{
            f"game_over_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_word_pulse(100, [g(), a(), m(), e1(), space(), o(), v(), e2(), r()]) * field_size * 0.1)
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


def draw_player1(x, y, a):
    move_cursor(x, y)
    play("player", 'screen')
    align()


def draw_player2(x, y, a):
    move_cursor(x, y)
    play("player", 'screen')
    align()


def draw_ship(x, y, a):
    move_cursor(x, y)
    play('ship' * get_rot_amp(a), 'screen')
    align()


def draw_ray(x, y, a):
    move_cursor(x, y)
    play('ray' , 'screen')
    align()


def draw_asteroid(x, y, a):
    move_cursor(x, y)
    play('asteroid' * get_rot_amp(a), 'screen')
    align()


def draw_game_over(x, y):
    move_cursor(x, y)
    play('game_over', 'screen')
    align()


def draw_border():
    move_cursor(0, 0)
    play('border', 'screen')
    align()


def get_distance(ax, ay, bx, by):
    distance = declare(fixed)
    distance = Math.sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by))
    return distance


def ray_hit(ray_x, ray_y, asteroid_x, asteroid_y):
    hit = declare(bool, False)

    distance = get_distance(ray_x, ray_y, asteroid_x, asteroid_y)

    with if_(distance < R_asteroid):
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


def get_inputs(p1, p2):
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

    assign(p1, IO1)
    assign(p2, IO2)
    if debug:
        save(p1, a_stream)
        save(p2, b_stream)

    return p1, p2


# %%

rng = np.random.default_rng(seed=1234)
# %%

with program() as game:
    draw_ball_b = declare(bool, True)
    rays_active = declare(bool, value=[False] + [False] * (N_rays - 1))
    rays_age = declare(fixed, value=[max_ray_age] + [0] * (N_rays - 1))
    rays_x = declare(fixed, value=[0] * N_rays)
    rays_y = declare(fixed, value=[0] * N_rays)
    rays_a = declare(fixed, value=[0] * N_rays)
    v_ray_x = declare(fixed, 0.2)
    v_ray_y = declare(fixed, 0.2)

    asteroids_active = declare(bool, value=[True] * N_asteroids)
    asteroids_x = declare(fixed, value=rng.uniform(-field_size, field_size, N_asteroids))
    asteroids_y = declare(fixed, value=rng.uniform(-field_size, field_size, N_asteroids))
    asteroids_a = declare(fixed, value=rng.uniform(-.5, .5, N_asteroids))
    ball_x = declare(fixed, 0)
    ball_y = declare(fixed, 0)
    ball_a = declare(fixed, 0)

    # spawn the ball
    assign(ball_x, 0)
    assign(ball_y, 0)
    assign(ball_a, 0)

    t = declare(fixed, 0)
    t_prim = declare(fixed, 0)
    t_last_ray_spawn = declare(fixed, -1.1)
    dt = declare(fixed, 0)
    i = declare(int, 0)
    j = declare(int, 0)

    p1 = declare(int)
    p2 = declare(int)
    p1_up = declare(fixed, 0)
    p2_up = declare(fixed, 0)
    p1_down = declare(fixed, 0)
    p2_down = declare(fixed, 0)
    p1_x = declare(fixed, -field_size*0.5)
    p1_vx = declare(fixed, 0)
    p2_x = declare(fixed, field_size*0.5)
    p2_vx = declare(fixed, 0)
    p1_y = declare(fixed, 0)
    p1_vy = declare(fixed, 0)
    p2_y = declare(fixed, 0)
    p2_vy = declare(fixed, 0)

    cont = declare(bool, True)
    crashed = declare(bool,False)

    if debug:
        a_stream = declare_stream()
        b_stream = declare_stream()

    # Game loop
    # with while_(t < 500*time_step_size):
    with while_(cont):
        assign(dt, t - t_prim)
        assign(t_prim, t)

        # process user inputs
        assign(p1, 0)  # The user input
        assign(p2, 0)  # The user input
        assign(p1_up, 0)
        assign(p2_up, 0)
        assign(p2_down, 0)
        assign(p1_down, 0)


        '''
        The inputs
        w - forward
        a - left
        d - right
        
        space - fire
        escape - end game
        '''

        get_inputs(p1, p2)
        with if_(p1 == 1):
            assign(p1_up, 1)
        with elif_(p1 == 2):
            assign(p1_down, -1)

        with if_(p2 == 3):
            assign(p2_up, 1)
        with elif_(p2 == 4):
            assign(p2_down, -1)

        # # update the velocity and position of the players
        assign(p1_y, p1_y + p1_vy * dt)
        assign(p2_y, p2_y + p2_vy * dt)
        assign(p1_vy, p1_vy + (p1_up+p1_down) * player_acceleration * dt)
        assign(p2_vy, p2_vy + (p2_up+p2_down) * player_acceleration * dt)
        clip_velocity(p1_vy)
        clip_velocity(p2_vy)

        # move the ball

        assign(ball_x, ball_x + v_ray_x * dt)
        assign(ball_y, ball_y + v_ray_y * dt)

        # process hits
        with if_((get_distance(ball_x, ball_y, p1_x, p1_y) < R_asteroid)):
            with if_(v_ray_y + p1_vy < 0.25):
                assign(v_ray_y, -1 * (v_ray_y + p1_vy))
                assign(v_ray_x, -1 * (v_ray_x))
            with else_():
                assign(v_ray_y, -1 * (0.25))
                assign(v_ray_x, -1 * (v_ray_x))
        with if_((get_distance(ball_x, ball_y, p2_x, p2_y) < R_asteroid)):
            with if_(v_ray_y + p1_vy < 0.25):
                assign(v_ray_y, -1 * (v_ray_y + p2_vy))
                assign(v_ray_x, -1 * (v_ray_x))
            with else_():
                assign(v_ray_y, -1 * (0.25))
                assign(v_ray_x, -1 * (v_ray_x))
        with if_(ball_x > field_size*0.7):
            assign(draw_ball_b, False)
        with elif_(ball_x < -field_size*0.7):
            assign(draw_ball_b, False)
        with if_(ball_y > field_size*0.7):
            assign(v_ray_y, -1 * (v_ray_y))
        with elif_(ball_y < -field_size*0.7):
            assign(v_ray_y, -1 * (v_ray_y))
        with if_(p1_y > field_size*0.7):
            assign(p1_y, field_size*0.7)
        with elif_(p1_y < -field_size*0.7):
            assign(p1_y, -field_size*0.7)
        with if_(p2_y > field_size*0.7):
            assign(p2_y, field_size*0.7)
        with elif_(p2_y < -field_size*0.7):
            assign(p2_y, -field_size*0.7)


        # draw graphics
        play("marker_pulse", "draw_marker_element")
        with if_(draw_ball_b):
            draw_player2(p2_x, p2_y, 0)
            draw_ray(ball_x, ball_y, 0)
            draw_player1(p1_x, p1_y, 0)
        with else_():
            draw_ray(0, 0, 0)
            draw_game_over(-0.15,0)


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
            elif event.key == keyboard.KeyCode.from_char('q'):
                send_over_io(1, 1, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('a'):
                send_over_io(1, 2, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('o'):
                send_over_io(2, 3, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('l'):
                send_over_io(2, 4, type(event) is events.Press)
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
