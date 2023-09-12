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
        wait(int(1e6//4), 'fake')  #  Wait a ms

        assign(key, IO1)
        with switch_(key):
            with case_(0):  # Nothing
                pass
            with case_(1):  # w
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
            with case_(2):  # s
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
            with case_(3):  # a
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
            with case_(4):  # d
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
            with case_(5):  # space
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
            with case_(6):  # crtl
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
            with case_(99):  # esc
                save(key, pressed_keys)
                assign(IO1, 0)
                assign(key, 0)
                assign(cond, False)

    with stream_processing():
        pressed_keys.save_all('pressed_keys')

qmm = QuantumMachinesManager('172.16.33.100', cluster_name='Cluster_81')
qm = qmm.open_qm(config)
job = qm.execute(io_example)
res = job.result_handles

while res.is_processing():
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
            if type(event) is events.Press:
                if event.key == keyboard.Key.esc:
                    qm.set_io1_value(99)
                    break
                elif event.key == keyboard.Key.space:
                    qm.set_io1_value(5)
                elif event.key == keyboard.Key.ctrl_l:
                    qm.set_io1_value(6)
                elif event.key == keyboard.KeyCode.from_char('w'):
                    qm.set_io1_value(1)
                elif event.key == keyboard.KeyCode.from_char('s'):
                    qm.set_io1_value(2)
                elif event.key == keyboard.KeyCode.from_char('a'):
                    qm.set_io1_value(3)
                elif event.key == keyboard.KeyCode.from_char('d'):
                    qm.set_io1_value(4)
                else:
                    pass

print(res.pressed_keys.fetch_all())