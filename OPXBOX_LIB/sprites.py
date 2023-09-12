import numpy as np
import matplotlib.pyplot as plt
import pytest


def resample_trace(x, y, points):
    assert len(x) == len(y)
    t = np.linspace(0, len(x), points)
    x = np.interp(t, np.arange(len(x)), x)
    y = np.interp(t, np.arange(len(y)), y)
    return np.array([x, y])


def calc_distances(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    return np.sqrt(np.square(y[:-1] - y[1:]) + np.square(x[:-1] - x[1:]))


def get_border_pulse(points):
    x = [0, 1, 1, 0, 0]
    y = [0, 0, 1, 1, 0]
    return resample_trace(x, y, points) * 2 - 1


def draw_example(pulse):
    plt.plot(*pulse)
    plt.show()


if __name__ == '__main__':
    draw_example(get_border_pulse(100))
