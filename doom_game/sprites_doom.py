import numpy as np

def resample_trace(x, y, points):
    """
    Resample the trace defined by x and y to a given number of points.
    """
    assert len(x) == len(y)
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def get_crosshair_pulse(points):
    """Generate a crosshair sprite for aiming"""
    xy = [
        # Horizontal line
        (-0.3, 0),
        (0.3, 0),
        (0, 0),  # Center
        # Vertical line
        (0, -0.3),
        (0, 0.3),
        (0, 0),  # Back to center
        # Inner circle
    ]
    # Add small circle in center
    n_circle = 12
    theta = np.linspace(0, 2*np.pi, n_circle)
    circle_x = 0.08 * np.cos(theta)
    circle_y = 0.08 * np.sin(theta)
    
    x = [coord[0] for coord in xy] + circle_x.tolist()
    y = [coord[1] for coord in xy] + circle_y.tolist()
    
    return resample_trace(x, y, points)

def get_enemy_pulse(points):
    """Generate an enemy sprite (demon-like figure)"""
    xy = [
        # Head outline
        (-0.4, 0.5),
        (-0.3, 0.7),
        (0.3, 0.7),
        (0.4, 0.5),
        # Horns
        (-0.3, 0.7),
        (-0.4, 0.9),
        (-0.3, 0.7),
        (0.3, 0.7),
        (0.4, 0.9),
        (0.3, 0.7),
        (0.4, 0.5),
        # Face features - angry eyes
        (0.15, 0.6),
        (0.25, 0.55),
        (0.25, 0.5),
        (0.15, 0.6),
        (-0.25, 0.55),
        (-0.15, 0.6),
        (-0.25, 0.5),
        (-0.25, 0.55),
        # Evil mouth
        (-0.2, 0.3),
        (-0.1, 0.25),
        (0, 0.3),
        (0.1, 0.25),
        (0.2, 0.3),
        (0, 0.3),
        # Neck
        (0, 0.15),
        # Body - muscular
        (-0.5, 0.15),
        (-0.6, -0.2),
        (-0.5, -0.5),
        # Right leg
        (-0.3, -0.5),
        (-0.3, -0.9),
        (-0.2, -0.9),
        (-0.2, -0.5),
        (-0.5, -0.5),
        # Body center to left side
        (0, -0.2),
        (0.5, -0.5),
        # Left leg
        (0.2, -0.5),
        (0.2, -0.9),
        (0.3, -0.9),
        (0.3, -0.5),
        (0.5, -0.5),
        # Back up right side of body
        (0.6, -0.2),
        (0.5, 0.15),
        (0, 0.15),
        # Arms
        (-0.5, 0.15),
        (-0.7, 0),
        (-0.9, -0.1),
        (-0.7, 0),
        (-0.5, 0.15),
        (0.5, 0.15),
        (0.7, 0),
        (0.9, -0.1),
        (0.7, 0),
        (0.5, 0.15),
        (0, 0.15),
        (0, 0.3),
        (-0.4, 0.5),
    ]
    
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

def get_wall_pulse(points):
    """Generate a wall segment for maze"""
    xy = [
        # Brick pattern
        (-1, 0.8),
        (1, 0.8),
        (1, 0.5),
        (-1, 0.5),
        (-1, 0.8),
        # Middle row
        (0, 0.8),
        (0, 0.5),
        (0, 0.2),
        (-1, 0.2),
        (-1, 0.5),
        (1, 0.5),
        (1, 0.2),
        (0, 0.2),
        (0, -0.1),
        (1, -0.1),
        (1, -0.4),
        (-1, -0.4),
        (-1, -0.1),
        (0, -0.1),
        (0, -0.8),
        (-1, -0.8),
        (-1, -0.1),
    ]
    
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

def get_bullet_pulse(points):
    """Generate a bullet/projectile sprite - energy ball"""
    # Outer circle
    n_outer = 15
    theta = np.linspace(0, 2*np.pi, n_outer)
    outer_x = 0.5 * np.cos(theta)
    outer_y = 0.5 * np.sin(theta)
    
    # Inner circle
    n_inner = 12
    theta_inner = np.linspace(0, 2*np.pi, n_inner)
    inner_x = 0.3 * np.cos(theta_inner)
    inner_y = 0.3 * np.sin(theta_inner)
    
    # Core
    n_core = 8
    theta_core = np.linspace(0, 2*np.pi, n_core)
    core_x = 0.15 * np.cos(theta_core)
    core_y = 0.15 * np.sin(theta_core)
    
    x = np.concatenate([outer_x, inner_x, core_x])
    y = np.concatenate([outer_y, inner_y, core_y])
    
    return resample_trace(x.tolist(), y.tolist(), points)

def get_health_pack_pulse(points):
    """Generate a health pack sprite (medkit with cross)"""
    xy = [
        # Box outline
        (-0.5, -0.4),
        (-0.5, 0.4),
        (0.5, 0.4),
        (0.5, -0.4),
        (-0.5, -0.4),
        # Cross - horizontal
        (-0.3, 0),
        (0.3, 0),
        (0, 0),
        # Cross - vertical
        (0, -0.3),
        (0, 0.3),
        (0, 0),
        # Latches
        (-0.5, 0.2),
        (-0.6, 0.2),
        (-0.6, 0.3),
        (-0.5, 0.3),
        (-0.5, 0.2),
        (-0.5, -0.2),
        (-0.6, -0.2),
        (-0.6, -0.3),
        (-0.5, -0.3),
        (-0.5, -0.2),
    ]
    
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

def get_door_pulse(points):
    """Generate a door sprite"""
    xy = [
        # Door frame
        (-0.6, -0.8),
        (-0.6, 0.8),
        (-0.5, 1.0),
        (0.5, 1.0),
        (0.6, 0.8),
        (0.6, -0.8),
        (-0.6, -0.8),
        # Door panels
        (-0.4, 0.6),
        (-0.4, 0.2),
        (0.4, 0.2),
        (0.4, 0.6),
        (-0.4, 0.6),
        (-0.4, -0.2),
        (0.4, -0.2),
        (0.4, -0.6),
        (-0.4, -0.6),
        (-0.4, -0.2),
        # Door handle
        (0.3, 0),
        (0.5, 0),
        (0.5, 0.1),
        (0.3, 0.1),
        (0.3, 0),
    ]
    
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

def get_border_pulse(points):
    """Generate border/viewport frame"""
    x = [0, 1, 1, 0, 0]
    y = [0, 0, 1, 1, 0]
    return resample_trace(x, y, points) * 2 - 1

def get_gun_pulse(points):
    """Generate gun sprite (player's weapon at bottom of screen) - shotgun style"""
    xy = [
        # Gun grip
        (-0.15, -0.9),
        (-0.15, -0.7),
        (-0.05, -0.7),
        (-0.05, -0.9),
        (-0.15, -0.9),
        # Trigger guard
        (-0.05, -0.75),
        (0, -0.8),
        (0.05, -0.75),
        (0.05, -0.7),
        (-0.05, -0.7),
        # Barrel - double barrel shotgun
        (-0.15, -0.7),
        (-0.15, -0.3),
        (-0.15, -0.4),
        (-0.25, -0.4),
        (-0.25, -0.3),
        (-0.15, -0.3),
        # Right barrel
        (0.05, -0.7),
        (0.05, -0.3),
        (0.05, -0.4),
        (0.15, -0.4),
        (0.15, -0.3),
        (0.05, -0.3),
        # Pump
        (-0.1, -0.5),
        (0.1, -0.5),
        (0.1, -0.45),
        (-0.1, -0.45),
        (-0.1, -0.5),
        # Barrel front
        (-0.15, -0.3),
        (0.05, -0.3),
    ]
    
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    return resample_trace(x, y, points)

# Letter sprites for text rendering - use same format as other games
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

def e2():
    return e1()

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
    """Convert letter coordinate lists into waveform pulses"""
    xy = []
    
    for i, letter in enumerate(letters):
        to_add = 0 if i == 0 else i * 1.25
        xy += [(item[0] + to_add, item[1]) for item in letter]
    
    x = [item[0] for item in xy]
    y = [item[1] for item in xy]
    return resample_trace(x, y, points)
