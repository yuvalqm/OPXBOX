import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *

from sprites import *

sprite_length = 100

user_input_pulse_length = 50000

field_size = 0.3  # V

input_probe_voltage = 0.2  # V

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
            'intermediate_frequency': 0,
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
            },
        },
        'draw_marker_element': {
            'singleInput': {
                'port': ('con1', 3),
            },
            'intermediate_frequency': 0,
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
            'intermediate_frequency': 0,
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
            for n in ["bird", "pillar", "border"]},
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
            f"border_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_border_pulse(sprite_length) * field_size)
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
qmm = QuantumMachinesManager(host=qop_ip, port=80)

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


def draw_border():
    move_cursor(0, 0)
    play('border', 'screen')
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


def process_border_collisions(x, y):
    for e in [x, y]:
        cycle_clip(e, field_size, -field_size)
    return x, y


def clip_angle(a):
    return cycle_clip(a, .5, -.5)


def clip_velocity(v):
    return clip(v, max_speed, -max_speed)


def get_inputs(player1, player2):
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

    assign(player1, IO1)
    assign(player2, IO2)
    if debug:
        save(player1, a_stream)
        save(player2, b_stream)

    return player1, player2


def send_over_io(io_num, value, set_value):
    if not set_value:
        value = 0
    if io_num == 1:
        qm.set_io1_value(value)
    elif io_num == 2:
        qm.set_io2_value(value)


if __name__ == '__main__':

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
