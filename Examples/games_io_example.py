from time import sleep
from pynput import keyboard
from qm import *
from qm.qua import *

config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                1: {"offset": 0.0},
            },
            "digital_outputs": {},
            "analog_inputs": {
            },
        }
    },
    "elements": {
        "fake": {
            "singleInput": {"port": ("con1", 1)},
            "intermediate_frequency": 50e6,
        },
    },
    "pulses": {
    },
    "waveforms": {
        "zero_wf": {"type": "constant", "sample": 0.0},
    },
    "digital_waveforms": {"ON": {"samples": [(1, 0)]}},
    "integration_weights": {
    },
}

with program() as io_example:
    key = declare(int)
    # nothing: 0
    # w: 1
    # s: 2
    # a: 3
    # d: 4
    # space: 5
    # crtl: 6
    # escape: 99
    pressed_keys = declare_stream()
    cond = declare(bool, value=True)

    with while_(cond):
        wait(int(1e6 // 4), 'fake')  # Wait a ms

        assign(key, IO1)
        with switch_(key):
            with case_(0):  # Nothing
                pass
            with case_(1):  # w
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                wait(int(60 // 4), 'fake')
            with case_(2):  # s
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                wait(int(60 // 4), 'fake')
            with case_(3):  # a
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                wait(int(60 // 4), 'fake')
            with case_(4):  # d
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                wait(int(60 // 4), 'fake')
            with case_(5):  # space
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                wait(int(60 // 4), 'fake')
            with case_(6):  # crtl
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                wait(int(60 // 4), 'fake')
            with case_(99):  # esc
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                assign(cond, False)
                wait(int(60 // 4), 'fake')

    with stream_processing():
        pressed_keys.save_all('pressed_keys')

qmm = QuantumMachinesManager('172.16.33.100', cluster_name='Cluster_81')
qm = qmm.open_qm(config)
job = qm.execute(io_example)
res = job.result_handles


def send_over_io(io_num, value, set_value):
    if not set_value:
        value = 0
    if io_num == 1:
        qm.set_io1_value(value)
    elif io_num == 2:
        qm.set_io2_value(value)


with keyboard.Events() as events:
    for event in events:
        # nothing: 0
        # w: 1
        # s: 2
        # a: 3
        # d: 4
        # space: 5
        # left crtl: 6
        # escape: 99
        if event.key == keyboard.Key.esc:
            send_over_io(1, 99, type(event) is events.Press)
            break
        elif event.key == keyboard.Key.space:
            send_over_io(1, 5, type(event) is events.Press)
        elif event.key == keyboard.Key.ctrl_l:
            send_over_io(1, 6, type(event) is events.Press)
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

a = res.pressed_keys.fetch_all()
print(a)
