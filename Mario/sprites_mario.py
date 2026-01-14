import numpy as np
import matplotlib.pyplot as plt

def resample_trace(x, y, points):
    """
    Resample the trace defined by x and y to a given number of points.
    """
    assert len(x) == len(y)
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

def get_mario_pulse(points):
    """
    Classic Mario sprite with hat, body, and legs.
    """
    # Hat/Cap (top)
    hat_x = [-0.4, -0.4, 0.4, 0.4, 0.3, -0.3, -0.4]
    hat_y = [0.5, 0.7, 0.7, 0.5, 0.5, 0.5, 0.5]
    
    # Face/Head
    face_x = [-0.3, -0.3, 0.3, 0.3, -0.3]
    face_y = [0.5, 0.2, 0.2, 0.5, 0.5]
    
    # Eyes (two small dots)
    eye1_x = [-0.15, -0.15, -0.10, -0.10, -0.15]
    eye1_y = [0.35, 0.40, 0.40, 0.35, 0.35]
    
    eye2_x = [0.10, 0.10, 0.15, 0.15, 0.10]
    eye2_y = [0.35, 0.40, 0.40, 0.35, 0.35]
    
    # Mustache
    mustache_x = [-0.2, 0, 0.2]
    mustache_y = [0.25, 0.20, 0.25]
    
    # Body (shirt)
    body_x = [-0.35, -0.35, 0.35, 0.35, -0.35]
    body_y = [0.2, -0.2, -0.2, 0.2, 0.2]
    
    # Overalls straps
    strap1_x = [-0.2, -0.15, -0.15, -0.2]
    strap1_y = [0.2, 0.1, -0.2, -0.2]
    
    strap2_x = [0.15, 0.2, 0.2, 0.15]
    strap2_y = [0.1, 0.2, -0.2, -0.2]
    
    # Legs
    leg1_x = [-0.25, -0.25, -0.15, -0.15, -0.25]
    leg1_y = [-0.2, -0.6, -0.6, -0.2, -0.2]
    
    leg2_x = [0.15, 0.15, 0.25, 0.25, 0.15]
    leg2_y = [-0.2, -0.6, -0.6, -0.2, -0.2]
    
    # Combine all parts
    x = np.concatenate([hat_x, face_x, eye1_x, eye2_x, mustache_x, 
                        body_x, strap1_x, strap2_x, leg1_x, leg2_x])
    y = np.concatenate([hat_y, face_y, eye1_y, eye2_y, mustache_y, 
                        body_y, strap1_y, strap2_y, leg1_y, leg2_y])
    
    return resample_trace(x, y, points)

def get_goomba_pulse(points):
    """
    Classic Goomba enemy - mushroom-like shape with face.
    """
    # Body (mushroom cap)
    n_cap = 15
    theta = np.linspace(0, np.pi, n_cap)
    cap_x = 0.4 * np.cos(theta)
    cap_y = 0.3 * np.sin(theta) + 0.3
    
    # Stem/body
    stem_x = [-0.25, -0.25, 0.25, 0.25, -0.25]
    stem_y = [0.3, -0.5, -0.5, 0.3, 0.3]
    
    # Angry eyes
    eye1_x = [-0.2, -0.1, -0.15]
    eye1_y = [0.15, 0.2, 0.1]
    
    eye2_x = [0.1, 0.2, 0.15]
    eye2_y = [0.2, 0.15, 0.1]
    
    # Frown
    frown_n = 10
    frown_theta = np.linspace(0, np.pi, frown_n)
    frown_x = 0.15 * np.cos(frown_theta)
    frown_y = -0.1 * np.sin(frown_theta) - 0.05
    
    # Feet
    foot1_x = [-0.25, -0.35, -0.35, -0.25]
    foot1_y = [-0.5, -0.5, -0.6, -0.6]
    
    foot2_x = [0.25, 0.35, 0.35, 0.25]
    foot2_y = [-0.5, -0.5, -0.6, -0.6]
    
    x = np.concatenate([cap_x, stem_x, eye1_x, eye2_x, frown_x, foot1_x, foot2_x])
    y = np.concatenate([cap_y, stem_y, eye1_y, eye2_y, frown_y, foot1_y, foot2_y])
    
    return resample_trace(x, y, points)

def get_block_pulse(points):
    """
    Classic Mario brick/block - simple rectangle with detail lines.
    """
    # Main rectangle
    block_x = [-0.5, -0.5, 0.5, 0.5, -0.5]
    block_y = [-0.5, 0.5, 0.5, -0.5, -0.5]
    
    # Horizontal dividing line
    h_line_x = [-0.5, 0.5]
    h_line_y = [0, 0]
    
    # Vertical dividing line
    v_line_x = [0, 0]
    v_line_y = [-0.5, 0.5]
    
    # Question mark (for mystery block)
    q_mark_x = [0, 0, -0.1, 0.1, 0, 0, 0, 0]
    q_mark_y = [0.3, 0.2, 0.1, 0.1, 0, -0.1, -0.2, -0.25]
    
    x = np.concatenate([block_x, h_line_x, v_line_x, q_mark_x])
    y = np.concatenate([block_y, h_line_y, v_line_y, q_mark_y])
    
    return resample_trace(x, y, points)

def get_ground_pulse(points):
    """
    Ground/floor platform - long horizontal rectangle.
    """
    ground_x = [-1.0, -1.0, 1.0, 1.0, -1.0]
    ground_y = [-0.3, 0, 0, -0.3, -0.3]
    
    return resample_trace(x, y, points)

def get_pipe_pulse(points, height=1):
    """
    Classic Mario pipe - green tube with lip at top.
    """
    pipe_width = 0.3
    lip_width = 0.4
    lip_height = 0.2
    
    xy = [
        # Bottom left
        (-pipe_width, -height),
        # Up left side
        (-pipe_width, 0),
        # Expand to lip left
        (-lip_width, 0),
        # Top of lip left
        (-lip_width, lip_height),
        # Across top
        (lip_width, lip_height),
        # Down right of lip
        (lip_width, 0),
        # Contract to pipe
        (pipe_width, 0),
        # Down right side
        (pipe_width, -height),
        # Across bottom
        (-pipe_width, -height),
    ]
    
    # Inner pipe detail (oval at top)
    n_oval = 10
    theta = np.linspace(0, 2*np.pi, n_oval)
    oval_x = 0.15 * np.cos(theta)
    oval_y = 0.1 * np.sin(theta) + 0.1
    
    x = [coord[0] for coord in xy] + oval_x.tolist()
    y = [coord[1] for coord in xy] + oval_y.tolist()
    
    return resample_trace(x, y, points)

def get_coin_pulse(points):
    """
    Spinning coin - circular with details.
    """
    # Outer circle
    n_circle = 20
    theta = np.linspace(0, 2*np.pi, n_circle)
    circle_x = 0.3 * np.cos(theta)
    circle_y = 0.3 * np.sin(theta)
    
    # Inner circle (smaller)
    n_inner = 15
    theta_inner = np.linspace(0, 2*np.pi, n_inner)
    inner_x = 0.2 * np.cos(theta_inner)
    inner_y = 0.2 * np.sin(theta_inner)
    
    x = np.concatenate([circle_x, inner_x])
    y = np.concatenate([circle_y, inner_y])
    
    return resample_trace(x, y, points)

def get_border_pulse(points):
    """
    Screen border.
    """
    x = [0, 1, 1, 0, 0]
    y = [0, 0, 1, 1, 0]
    return resample_trace(x, y, points) * 2 - 1

def get_game_over_text(points):
    """
    'GAME OVER' text for Mario style.
    """
    # Reuse letter functions from flappy bird but arrange differently
    xy = []
    
    # G
    g_coords = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5), (0.5, -0.5), 
                (0.5, 0), (0, 0), (0.5, 0)]
    
    # A
    a_coords = [(-0.5, -0.5), (0, 0.5), (0.5, -0.5), (0.25, 0), 
                (-0.25, 0), (0.25, 0)]
    
    # M
    m_coords = [(-0.5, -0.5), (-0.25, 0.5), (0, -0.5), (0.25, 0.5), (0.5, -0.5)]
    
    # E
    e_coords = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (-0.5, 0.5), 
                (-0.5, 0), (0.5, 0), (-0.5, 0), (-0.5, -0.5), (0.5, -0.5)]
    
    # Space between words
    space_coords = [(-0.5, -0.5), (0.5, -0.5)]
    
    letters = [g_coords, a_coords, m_coords, e_coords, space_coords,
               # OVER
               [(-0.5, 0.5), (-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)],  # O
               [(-0.5, 0.5), (0, -0.5), (0.5, 0.5)],  # V
               e_coords,  # E
               [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, 0), (-0.5, 0), (0.5, -0.5)]]  # R
    
    for i, letter in enumerate(letters):
        offset = i * 1.2
        xy += [(coord[0] + offset, coord[1]) for coord in letter]
    
    x = [coord[0] for coord in xy]
    y = [coord[1] for coord in xy]
    
    return resample_trace(x, y, points)

def draw_example(pulse, title="Sprite"):
    """Utility function to visualize sprites."""
    plt.figure(figsize=(8, 6))
    plt.plot(pulse[0], pulse[1], linewidth=2)
    plt.title(title)
    plt.axis('equal')
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == '__main__':
    # Test all sprites
    print("Testing Mario sprites...")
    sprites = [
        (get_mario_pulse(1000), "Mario"),
        (get_goomba_pulse(1000), "Goomba Enemy"),
        (get_block_pulse(1000), "Block"),
        (get_pipe_pulse(1000, 2), "Pipe"),
        (get_coin_pulse(1000), "Coin"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, (sprite, name) in enumerate(sprites):
        axes[idx].plot(sprite[0], sprite[1], linewidth=2)
        axes[idx].set_title(name, fontweight='bold')
        axes[idx].axis('equal')
        axes[idx].grid(True, alpha=0.3)
    
    axes[-1].axis('off')
    plt.tight_layout()
    plt.savefig('mario_sprites.png', dpi=150)
    print("✓ Saved mario_sprites.png")
