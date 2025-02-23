import numpy as np

def resample_trace(x, y, points):
    """Helper to resample a trace to a specific number of points."""
    import numpy as np
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def get_mario_pulse(points=100):
    """
    A super-simplified "Mario" shape. 
    In reality you'd want more detail.
    """
    # Just a small shape: a circle-ish loop
    t = np.linspace(0, 2*np.pi, 10)
    r = 0.4
    x = r * np.cos(t)
    y = r * np.sin(t)
    return resample_trace(x, y, points)

def get_block_pulse(points=100):
    """Square block shape."""
    xy = [
        (-0.5, -0.5),
        (-0.5,  0.5),
        ( 0.5,  0.5),
        ( 0.5, -0.5),
        (-0.5, -0.5),
    ]
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]
    return resample_trace(x, y, points)

def get_enemy_pulse(points=100):
    """Simple triangular shape for an enemy."""
    xy = [
        (-0.5, -0.3),
        ( 0.5, -0.3),
        ( 0.0,  0.5),
        (-0.5, -0.3),
    ]
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]
    return resample_trace(x, y, points)

def get_ground_pulse(points=100):
    """A simple horizontal rectangle representing the ground."""
    xy = [
        (-1, 0),
        (-1, 0.2),
        ( 1, 0.2),
        ( 1, 0),
        (-1, 0),
    ]
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]
    return resample_trace(x, y, points)

def get_border_pulse(points=100):
    """A border that goes around the screen edges."""
    xy = [
        (-1, -1),
        (-1,  1),
        ( 1,  1),
        ( 1, -1),
        (-1, -1),
    ]
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]
    return resample_trace(x, y, points)
