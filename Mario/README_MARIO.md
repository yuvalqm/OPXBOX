# Super Mario OPXBOX Game

A Mario-style platformer game running on the OPX quantum controller, similar to the Flappy Bird implementation.

## Game Description

Classic Mario-style side-scrolling game where Mario automatically runs forward and must jump over obstacles (Goombas and Pipes). The game uses vector graphics displayed on an oscilloscope via the OPX controller.

## Features

- **Mario Character**: Classic Mario sprite with hat, mustache, overalls, and legs
- **Obstacles**: 
  - Goombas (mushroom enemies)
  - Green pipes (from classic Mario games)
- **Physics**: 
  - Gravity-based jumping mechanics
  - Ground collision detection
  - Obstacle collision detection
- **Scoring**: Points awarded for each obstacle successfully passed

## Controls

- **SPACE**: Jump
- **ESC**: Quit game

## Game Mechanics

1. Mario stays at a fixed horizontal position
2. Obstacles scroll from right to left
3. Press SPACE to jump over obstacles
4. Game ends if Mario collides with an obstacle
5. Obstacles respawn on the right side after passing

## Files

- `mario_new.py`: Main game implementation with QUA program
- `sprites_mario.py`: Sprite definitions for all game objects
  - `get_mario_pulse()`: Mario character
  - `get_goomba_pulse()`: Goomba enemy
  - `get_pipe_pulse()`: Green pipe obstacle
  - `get_block_pulse()`: Question block
  - `get_coin_pulse()`: Collectible coin
  - `get_game_over_text()`: Game over screen

## Configuration Parameters

Key parameters in `mario_new.py`:

```python
FIELD_SIZE = 0.3           # Display field size in volts
N_OBSTACLES = 5            # Number of obstacles on screen
GRAVITY = 0.4              # Gravity strength
JUMP_FORCE = 0.25          # Jump height
V_OBSTACLE = 0.15          # Obstacle scroll speed
TIME_STEP_SIZE = 0.01      # Physics update rate
```

## How It Works

Similar to the Flappy Bird implementation:

1. **QUA Configuration**: Defines analog outputs for X/Y oscilloscope control
2. **Sprite Generation**: Uses `resample_trace()` to create smooth waveforms
3. **Game Loop**: 
   - Reads user input via IO2
   - Updates Mario physics (gravity, jumping)
   - Moves obstacles left
   - Checks collisions
   - Draws all sprites to oscilloscope
4. **Display**: Sprites drawn using arbitrary waveforms on IQ outputs

## Differences from Flappy Bird

- **Horizontal scrolling**: Obstacles move left instead of pillars moving in 2D
- **Ground mechanics**: Mario walks on ground, can only jump when grounded
- **Multiple obstacle types**: Goombas and pipes with different sprites
- **Simpler collision**: Bounding box detection instead of circular

## Running the Game

```bash
cd ~/repos/OPXBOX/Mario
python3 mario_new.py
```

Make sure the OPX controller is connected at IP `172.16.33.107`.

## Future Enhancements

Possible additions:
- [ ] Collectible coins
- [ ] Power-ups (mushrooms, stars)
- [ ] Different enemy types
- [ ] Multiple ground levels
- [ ] Background scenery
- [ ] Sound effects via additional channels
- [ ] High score tracking

## Credits

Based on the OPXBOX Flappy Bird implementation structure.
Sprites designed to match classic Super Mario Bros aesthetic.
