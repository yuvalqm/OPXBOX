import numpy as np
import matplotlib.pyplot as plt
import pytest

def resample_trace(x, y, points):
    """
    Resample the trace defined by x and y to a given number of points.
    """
    assert len(x) == len(y)
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def calc_distances(x, y):
    """
    Calculate distances between consecutive points.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    return np.sqrt(np.square(np.diff(x)) + np.square(np.diff(y)))

@pytest.mark.parametrize("x, y, exp", [
    ([0, 0], [0, 0], 0),
    ([0, 0], [1, 1], 0),
    ([0, 1], [0, 0], 1),
    ([0, 0], [1, 0], 1),
    ([0, 0], [0, 1], 1),
    ([0, 1], [0, 1], np.sqrt(2)),
    ([1, 0], [1, 0], np.sqrt(2)),
])
def test_distances(x, y, exp):
    res = calc_distances(x, y)
    assert res.shape == (1,)
    assert res[0] == pytest.approx(exp)

def sample_with_speed(x, y, speed):
    """
    Sample the trace with a given speed (in sample/volt).
    """
    assert len(x) == len(y)
    distances = calc_distances(x, y)
    cumdis = np.cumsum(distances)
    # TODO: Implement sampling with speed adjustment
    raise NotImplementedError("sample_with_speed function is not implemented yet.")
    # return resample_trace(x, y, int(cumdis[-1] * speed))

def get_ship_pulse(points):
    x = [-0.5, -1, 1, -1, -0.5]
    y = [0, -0.5, 0, 0.5, 0]
    return resample_trace(x, y, points)

def get_ray_pulse(points):
    x = [-0.5, 0.5]
    y = [0, 0]
    return resample_trace(x, y, points)

def get_asteroid_pulse(points, seed=5, arms=10):
    t = np.linspace(0, 1, arms + 1)[:-1] * 2 * np.pi
    rng = np.random.default_rng(seed=seed)
    r = rng.uniform(-0.4, 0.4, arms)
    phi = rng.uniform(-0.02, 0.02, arms) * 2 * np.pi
    x = np.cos(t + phi) * (1 + r)
    y = np.sin(t + phi) * (1 + r)
    # Close the loop
    x = np.append(x, x[0])
    y = np.append(y, y[0])
    return resample_trace(x, y, points)

def get_border_pulse(points):
    x = [0, 1, 1, 0, 0]
    y = [0, 0, 1, 1, 0]
    return resample_trace(x, y, points) * 2 - 1

def get_pillar_pulse(points, pillar_height=1, reverse=1):
    xy = [
        (-0.2, -pillar_height * reverse),
        (-0.2, pillar_height * reverse),
        (-0.3, pillar_height * reverse),
        (-0.3, (pillar_height + 0.4) * reverse),
        (0.3, (pillar_height + 0.4) * reverse),
        (0.3, pillar_height * reverse),
        (0.2, pillar_height * reverse),
        (0.2, -pillar_height * reverse),
    ]
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

def get_bird2_pulse(points):
    xy = [
        (-0.5, 0.5),
        (0, 0.75),
        (0.5, 0.5),
        # eye
        (0.25, 0.6),
        (0, 0.45),
        (-0.1, 0.2),
        (0, 0),
        (0.25, -0.1),
        (0.5, 0),
        (0.6, 0.25),
        (0.5, 0.5),
        # end eye
        (0.75, 0),
        # beak
        (1.25, -0.15),
        (1.25, -0.25),
        (1.25, -0.30),
        (0.5, -0.30),
        (0.75, 0),
        (0.5, -0.30),
        (0.5, -0.5),
        (0.5, -0.30),
        (1.25, -0.30),
        (1.2, -0.45),
        # end beak
        (0.5, -0.5),
        (0, -0.75),
        (-0.2, -0.75),
        (-0.5, -0.75),
        (-0.25, -0.5),
        # start wing
        (-0.25, -0.25),
        (-0.75, 0),
        (-1.25, -0.25),
        (-1.25, -0.5),
        (-0.9, -0.75),
        (-0.5, -0.75),
        (-0.25, -0.5),
        (-0.25, -0.25),
        # end wing
        (-0.75, 0),
        (-0.5, 0.5)
    ]
    # Scale the pulse
    x = [coord[0] * 0.5 for coord in xy]
    y = [coord[1] * 0.5 for coord in xy]
    return resample_trace(x, y, points)

def get_bird_pulse(points):
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
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

def g():
    xy = [
        (0.5, 0.5),
        (-0.5, 0.5),
        (-0.5, -0.5),
        (0.5, -0.5),
        (0.5, 0),
        (0, 0),
        (0.5, 0),
        (0.5, -0.5),
    ]

    return xy


def a():
    xy = [
        (-0.5, -0.5),
        (0, 0.5),
        (0.5, -0.5),
        (0.25, 0),
        (-0.25, 0),
        (0.25, 0),
        (0.5, -0.5),
    ]

    return xy


def m():
    xy = [
        (-0.5, -0.5),
        (-0.25, 0.5),
        (0, -0.5),
        (0.25, 0.5),
        (0.5, -0.5),
    ]

    return xy


def e1():
    xy = [
        (-0.5, -0.5),
        (-0.5, 0.5),
        (0.5, 0.5),
        (-0.5, 0.5),
        (-0.5, 0),
        (0.5, 0),
        (-0.5, 0),
        (-0.5, -0.5),
        (0.5, -0.5),
    ]

    return xy


def o():
    xy = [
        (-0.5, 0.5),
        (-0.5, -0.5),
        (0.5, -0.5),
        (0.5, 0.5),
        (-0.5, 0.5),
        (0.5, 0.5),
    ]

    return xy


def v():
    xy = [
        (-0.5, 0.5),
        (0, -0.5),
        (0.5, 0.5),

    ]

    return xy


def e2():
    xy = [
        (-0.5, 0.5),
        (0.5, 0.5),
        (-0.5, 0.5),
        (-0.5, 0),
        (0.5, 0),
        (-0.5, 0),
        (-0.5, -0.5),
        (0.5, -0.5),
    ]

    return xy


def r():
    xy = [
        (-0.5, -0.5),
        (-0.5, 0.5),
        (0.5, 0.5),
        (0.5, 0),
        (-0.5, 0),
        (0.5, -0.5),
    ]

    return xy


def space():
    xy = [
        (-0.5, -0.5),
        (0.5, -0.5),
    ]

    return xy


def get_word_pulse(points, letters):
    xy = []

    for i, letter in enumerate(letters):
        to_add = 0 if i == 0 else i * 1.5
        xy += [(item[0] + to_add, item[1]) for item in letter]

    x = [item[0] for item in xy]
    y = [item[1] for item in xy]
    return resample_trace(x, y, points)


def get_word_pulse(points, letters):
    xy = []

    for i, letter in enumerate(letters):
        to_add = 0 if i == 0 else i * 1.25
        xy += [(item[0] + to_add, item[1]) for item in letter]

    x = [item[0] for item in xy]
    y = [item[1] for item in xy]
    return resample_trace(x, y, points)

def draw_example(pulse):
    plt.plot(pulse[0], pulse[1])
    plt.show()

if __name__ == '__main__':
    draw_example(get_ship_pulse(100))
    draw_example(get_ray_pulse(100))
    draw_example(get_pillar_pulse(100))
    draw_example(get_border_pulse(100))
