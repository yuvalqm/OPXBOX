import numpy as np
import matplotlib.pyplot as plt
from pynput import keyboard

from qm import QuantumMachinesManager
from qm.qua import *
from sprites_doom import *

# =============================================================================
# Configuration Parameters
# =============================================================================
DEBUG = False
CONTROLLER = False

# Field and object parameters
FIELD_SIZE = 0.3           # V, size of the field
N_ENEMIES = 5              # Number of enemies
N_BULLETS = 10             # Max number of bullets
R_ENEMY = FIELD_SIZE * 0.1  # V, radius of enemies
R_BULLET = FIELD_SIZE * 0.02  # V, radius of bullets

# Player parameters
PLAYER_SPEED = 0.3         # V/s, player movement speed
ROTATION_SPEED = 2.0       # rad/s, player rotation speed

# Enemy parameters
ENEMY_SPEED = 0.1          # V/s, enemy movement speed
ENEMY_DAMAGE = 20          # Damage per hit

# Weapon parameters
BULLET_SPEED = 0.5         # V/s, bullet speed
BULLET_LIFETIME = 2.0      # s, how long bullets last
FIRE_COOLDOWN = 0.3        # s, time between shots

# Game parameters
PLAYER_MAX_HEALTH = 100
PLAYER_START_X = 0.0
PLAYER_START_Y = 0.0

# Timing parameters
TIME_STEP_SIZE = 0.01      # s, time advanced per tick
USER_INPUT_PULSE_LENGTH = 500000  # ns
SPRITE_LENGTH = 100        # number of samples for sprites
WAIT_TIME = 1e7 / 2        # ns, wait after drawing

# Controller parameters
INPUT_PROBE_VOLTAGE = 0.5  # V

# =============================================================================
# QUA Configuration
# =============================================================================
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
                "crosshair": "crosshair",
                "enemy": "enemy",
                "wall": "wall",
                "bullet": "bullet",
                "health": "health",
                "door": "door",
                "border": "border",
                "gun": "gun",
                "game_over": "game_over",
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
            'length': SPRITE_LENGTH,
            'waveforms': {k: f"{n}_{l}" for k, l in zip(["I", "Q"], ["x", "y"])},
        } for n in ["crosshair", "enemy", "wall", "bullet", "health", "door", "border", "gun", "game_over"]},
        "measure_user_input": {
            "operation": "measurement",
            'length': USER_INPUT_PULSE_LENGTH,
            "integration_weights": {
                "constant": "cosine_weights",
            },
            'waveforms': {"single": "input_wf"},
        },
        "marker_pulse": {
            "operation": "control",
            'length': SPRITE_LENGTH,
            'waveforms': {"single": "marker_wf"},
        }
    },
    'waveforms': {
        **{
            f"crosshair_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_crosshair_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.3)
        },
        **{
            f"enemy_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_enemy_pulse(SPRITE_LENGTH) * R_ENEMY)
        },
        **{
            f"wall_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_wall_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.4)
        },
        **{
            f"bullet_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_bullet_pulse(SPRITE_LENGTH) * R_BULLET)
        },
        **{
            f"health_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_health_pack_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.08)
        },
        **{
            f"door_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_door_pulse(SPRITE_LENGTH) * FIELD_SIZE * 0.3)
        },
        **{
            f"border_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_border_pulse(SPRITE_LENGTH) * FIELD_SIZE)
        },
        **{
            f"gun_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], get_gun_pulse(SPRITE_LENGTH) * FIELD_SIZE)
        },
        **{
            f"game_over_{a}": {'type': 'arbitrary', 'samples': v}
            for a, v in zip(["x", "y"], 
                          get_word_pulse(SPRITE_LENGTH, [g(), a(), m(), e1(), space(), 
                                                          o(), v(), e2(), r()]) * FIELD_SIZE * 0.1)
        },
        'marker_wf': {"type": "constant", "sample": 0.2},
        'input_wf': {"type": "constant", "sample": INPUT_PROBE_VOLTAGE},
    },
    'digital_waveforms': {
        'draw_trigger': {'samples': [(1, 0)]}
    },
    "integration_weights": {
        "cosine_weights": {
            "cosine": [(1.0, USER_INPUT_PULSE_LENGTH)],
            "sine": [(0.0, USER_INPUT_PULSE_LENGTH)],
        },
    },
}

# =============================================================================
# QUA Machine Setup
# =============================================================================
qop_ip = '192.168.116.171'
qmm = QuantumMachinesManager(host=qop_ip, port=80)
qm = qmm.open_qm(configuration)

# =============================================================================
# Graphics and Utility Functions
# =============================================================================
def move_cursor(x, y):
    """Set cursor position on screen"""
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)

def get_rot_amp(a):
    """Calculate rotation amplitude based on angle"""
    return amp(Math.cos2pi(a), -Math.sin2pi(a), 
               Math.sin2pi(a), Math.cos2pi(a))

def draw_sprite(name, x, y, angle=0):
    """Draw sprite at position with rotation"""
    move_cursor(x, y)
    if angle != 0:
        play(name * get_rot_amp(angle), 'screen')
    else:
        play(name, 'screen')
    align()

def draw_crosshair():
    draw_sprite("crosshair", 0, 0)

def draw_enemy(x, y, angle):
    draw_sprite("enemy", x, y, angle)

def draw_bullet(x, y):
    draw_sprite("bullet", x, y)

def draw_gun():
    draw_sprite("gun", 0, -FIELD_SIZE * 0.7)

def draw_border():
    draw_sprite("border", 0, 0)

def draw_game_over():
    draw_sprite("game_over", -0.15, 0)

def get_distance(ax, ay, bx, by):
    """Calculate distance between two points"""
    distance = declare(fixed)
    distance = Math.sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by))
    return distance

def clip(x, upper, lower):
    """Clip value to range"""
    with if_(x > upper):
        assign(x, upper)
    with elif_(x < lower):
        assign(x, lower)
    return x

def cycle_clip(x, upper, lower):
    """Wrap value around boundaries"""
    with if_(x > upper):
        assign(x, lower)
    with elif_(x < lower):
        assign(x, upper)
    return x

def get_inputs(p1, p2):
    """Get player inputs from IO"""
    assign(p1, IO1)
    assign(p2, IO2)
    if DEBUG:
        save(p1, a_stream)
        save(p2, b_stream)
    return p1, p2

# =============================================================================
# Game Program
# =============================================================================
rng = np.random.default_rng(seed=42)

with program() as doom_game:
    # Player state
    player_x = declare(fixed, PLAYER_START_X)
    player_y = declare(fixed, PLAYER_START_Y)
    player_angle = declare(fixed, 0)  # Facing direction
    player_health = declare(int, PLAYER_MAX_HEALTH)
    player_alive = declare(bool, True)
    
    # Enemy state
    enemies_active = declare(bool, value=[True] * N_ENEMIES)
    enemies_x = declare(fixed, value=rng.uniform(-FIELD_SIZE*0.8, FIELD_SIZE*0.8, N_ENEMIES))
    enemies_y = declare(fixed, value=rng.uniform(-FIELD_SIZE*0.8, FIELD_SIZE*0.8, N_ENEMIES))
    enemies_angle = declare(fixed, value=rng.uniform(-0.5, 0.5, N_ENEMIES))
    enemies_health = declare(int, value=[100] * N_ENEMIES)
    
    # Bullet state
    bullets_active = declare(bool, value=[False] * N_BULLETS)
    bullets_x = declare(fixed, value=[0.0] * N_BULLETS)
    bullets_y = declare(fixed, value=[0.0] * N_BULLETS)
    bullets_vx = declare(fixed, value=[0.0] * N_BULLETS)
    bullets_vy = declare(fixed, value=[0.0] * N_BULLETS)
    bullets_age = declare(fixed, value=[0.0] * N_BULLETS)
    
    # Game state
    t = declare(fixed, 0)
    t_prev = declare(fixed, 0)
    t_last_shot = declare(fixed, -1.0)
    dt = declare(fixed, 0)
    i = declare(int, 0)
    j = declare(int, 0)
    
    # Input state
    p1 = declare(int)
    p2 = declare(int)
    ui_forward = declare(fixed, 0)
    ui_backward = declare(fixed, 0)
    ui_left = declare(fixed, 0)
    ui_right = declare(fixed, 0)
    ui_fire = declare(bool, False)
    
    cont = declare(bool, True)
    game_over = declare(bool, False)
    
    if DEBUG:
        a_stream = declare_stream()
        b_stream = declare_stream()
    
    # Main game loop
    with while_(cont):
        assign(dt, t - t_prev)
        assign(t_prev, t)
        
        # Process inputs
        assign(p1, 0)
        assign(p2, 0)
        assign(ui_forward, 0)
        assign(ui_backward, 0)
        assign(ui_left, 0)
        assign(ui_right, 0)
        assign(ui_fire, False)
        
        get_inputs(p1, p2)
        
        # Map inputs: w=1, s=2, a=3, d=4, space=5, esc=10
        with if_(p1 == 1):
            assign(ui_forward, 1)
        with elif_(p1 == 2):
            assign(ui_backward, 1)
        with elif_(p1 == 3):
            assign(ui_left, 1)
        with elif_(p1 == 4):
            assign(ui_right, 1)
        
        with if_(p2 == 5):
            assign(ui_fire, True)
        with elif_(p2 == 10):
            assign(cont, False)
        
        # Update player movement
        with if_(player_alive):
            # Forward/backward movement
            forward_x = declare(fixed, 0)
            forward_y = declare(fixed, 0)
            assign(forward_x, Math.cos2pi(player_angle) * PLAYER_SPEED * dt)
            assign(forward_y, Math.sin2pi(player_angle) * PLAYER_SPEED * dt)
            
            with if_(ui_forward == 1):
                assign(player_x, player_x + forward_x)
                assign(player_y, player_y + forward_y)
            with if_(ui_backward == 1):
                assign(player_x, player_x - forward_x)
                assign(player_y, player_y - forward_y)
            
            # Rotation
            with if_(ui_left == 1):
                assign(player_angle, player_angle + ROTATION_SPEED * dt / (2 * 3.14159))
            with if_(ui_right == 1):
                assign(player_angle, player_angle - ROTATION_SPEED * dt / (2 * 3.14159))
            
            # Keep player in bounds
            clip(player_x, FIELD_SIZE * 0.9, -FIELD_SIZE * 0.9)
            clip(player_y, FIELD_SIZE * 0.9, -FIELD_SIZE * 0.9)
            cycle_clip(player_angle, 0.5, -0.5)
            
            # Fire weapon
            can_fire = declare(bool, False)
            with if_((t - t_last_shot) > FIRE_COOLDOWN):
                assign(can_fire, True)
            
            with if_(ui_fire & can_fire):
                # Find inactive bullet slot
                with for_(i, 0, i < N_BULLETS, i + 1):
                    with if_(~bullets_active[i]):
                        assign(bullets_active[i], True)
                        assign(bullets_x[i], player_x)
                        assign(bullets_y[i], player_y)
                        assign(bullets_vx[i], Math.cos2pi(player_angle) * BULLET_SPEED)
                        assign(bullets_vy[i], Math.sin2pi(player_angle) * BULLET_SPEED)
                        assign(bullets_age[i], 0)
                        assign(t_last_shot, t)
                        assign(i, N_BULLETS)  # Break loop
        
        # Update bullets
        with for_(i, 0, i < N_BULLETS, i + 1):
            with if_(bullets_active[i]):
                assign(bullets_x[i], bullets_x[i] + bullets_vx[i] * dt)
                assign(bullets_y[i], bullets_y[i] + bullets_vy[i] * dt)
                assign(bullets_age[i], bullets_age[i] + dt)
                
                # Deactivate old bullets or out of bounds
                with if_((bullets_age[i] > BULLET_LIFETIME) | 
                        (Math.abs(bullets_x[i]) > FIELD_SIZE) |
                        (Math.abs(bullets_y[i]) > FIELD_SIZE)):
                    assign(bullets_active[i], False)
        
        # Update enemies
        with for_(i, 0, i < N_ENEMIES, i + 1):
            with if_(enemies_active[i]):
                # Move enemies toward player
                dx = declare(fixed, 0)
                dy = declare(fixed, 0)
                dist = declare(fixed, 0)
                
                assign(dx, player_x - enemies_x[i])
                assign(dy, player_y - enemies_y[i])
                assign(dist, Math.sqrt(dx * dx + dy * dy))
                
                # Normalize and move
                with if_(dist > 0.01):
                    assign(enemies_x[i], enemies_x[i] + (dx / dist) * ENEMY_SPEED * dt)
                    assign(enemies_y[i], enemies_y[i] + (dy / dist) * ENEMY_SPEED * dt)
                
                # Check collision with player
                player_dist = get_distance(player_x, player_y, enemies_x[i], enemies_y[i])
                with if_(player_dist < R_ENEMY):
                    assign(player_health, player_health - 1)
                    with if_(player_health <= 0):
                        assign(player_alive, False)
                        assign(game_over, True)
        
        # Check bullet-enemy collisions
        with for_(i, 0, i < N_BULLETS, i + 1):
            with if_(bullets_active[i]):
                with for_(j, 0, j < N_ENEMIES, j + 1):
                    with if_(enemies_active[j]):
                        hit_dist = get_distance(bullets_x[i], bullets_y[i], 
                                               enemies_x[j], enemies_y[j])
                        with if_(hit_dist < R_ENEMY):
                            assign(bullets_active[i], False)
                            assign(enemies_health[j], enemies_health[j] - 34)
                            with if_(enemies_health[j] <= 0):
                                assign(enemies_active[j], False)
        
        # Draw everything
        play("marker_pulse", "draw_marker_element")
        
        with if_(game_over):
            draw_game_over()
        with else_():
            # Draw enemies
            with for_(i, 0, i < N_ENEMIES, i + 1):
                with if_(enemies_active[i]):
                    draw_enemy(enemies_x[i], enemies_y[i], enemies_angle[i])
            
            # Draw bullets
            with for_(i, 0, i < N_BULLETS, i + 1):
                with if_(bullets_active[i]):
                    draw_bullet(bullets_x[i], bullets_y[i])
            
            # Draw HUD elements
            draw_crosshair()
            draw_gun()
            draw_border()
        
        align()
        wait(int(WAIT_TIME))
        assign(t, t + TIME_STEP_SIZE)
    
    if DEBUG:
        with stream_processing():
            a_stream.save_all('move')
            b_stream.save_all('act')

# =============================================================================
# IO Functions
# =============================================================================
def send_over_io(io_num, value, set_value):
    """Send input values over IO"""
    if not set_value:
        value = 0
    if io_num == 1:
        qm.set_io1_value(value)
    elif io_num == 2:
        qm.set_io2_value(value)

# =============================================================================
# Main Execution
# =============================================================================
if __name__ == '__main__':
    job = qm.execute(doom_game)
    res = job.result_handles
    
    print('DOOM Game Starting!')
    print('Controls:')
    print('  W - Move forward')
    print('  S - Move backward')
    print('  A - Rotate left')
    print('  D - Rotate right')
    print('  SPACE - Fire weapon')
    print('  ESC - Quit game')
    
    with keyboard.Events() as events:
        for event in events:
            # Input mapping:
            # w: 1, s: 2, a: 3, d: 4
            # space: 5, esc: 10
            
            if event.key == keyboard.Key.esc:
                send_over_io(2, 10, type(event) is events.Press)
                break
            elif event.key == keyboard.Key.space:
                send_over_io(2, 5, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('w'):
                send_over_io(1, 1, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('s'):
                send_over_io(1, 2, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('a'):
                send_over_io(1, 3, type(event) is events.Press)
            elif event.key == keyboard.KeyCode.from_char('d'):
                send_over_io(1, 4, type(event) is events.Press)
    
    if DEBUG:
        res.wait_for_all_values()
        move = res.move.fetch_all()
        act = res.act.fetch_all()
        plt.plot(move, label='Movement')
        plt.plot(act, label='Actions')
        plt.legend()
        plt.show()
