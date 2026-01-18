# DOOM-like Game for OPXBOX

A first-person shooter game inspired by DOOM, implemented using the Quantum Machines QUA framework with vector graphics rendering.

## Game Description

This is a Doom-style FPS game where you battle enemies in a top-down perspective (simplified from true 3D FPS). The player navigates the arena, shoots enemies, and tries to survive as long as possible.

## Features

- **Player Movement**: Move forward/backward and rotate to aim
- **Shooting Mechanics**: Fire projectiles at enemies with cooldown system
- **Enemy AI**: Enemies track and move toward the player
- **Health System**: Player takes damage from enemy contact
- **Collision Detection**: Bullets hit enemies, enemies hit player
- **Game Over**: Ends when player health reaches zero
- **Vector Graphics**: All sprites rendered using oscilloscope-style vector graphics

## Controls

- **W** - Move forward
- **S** - Move backward  
- **A** - Rotate left (turn counterclockwise)
- **D** - Rotate right (turn clockwise)
- **SPACE** - Fire weapon
- **ESC** - Quit game

## Game Elements

### Player
- Starts at center with 100 health
- Can move and rotate in the arena
- Fires projectiles in the direction facing
- Dies when health reaches 0

### Enemies
- 5 enemies spawn in random positions
- Move toward the player continuously
- Deal damage on contact with player
- Each has 100 health and dies after taking enough damage
- Represented as demon-like vector sprites

### Bullets
- Maximum of 10 bullets can exist at once
- Fire cooldown of 0.3 seconds between shots
- Bullets last for 2 seconds before disappearing
- Deal 34 damage per hit to enemies
- Deactivate when hitting enemy or going out of bounds

### HUD
- Crosshair in center for aiming
- Gun sprite at bottom of screen
- Border showing the play area
- Game Over text when player dies

## Technical Details

### Configuration
- Field size: 0.3V
- Player speed: 0.3 V/s
- Rotation speed: 2.0 rad/s
- Enemy speed: 0.1 V/s
- Bullet speed: 0.5 V/s
- Time step: 0.01s per game tick

### Sprites
All sprites are defined in `sprites_doom.py`:
- Crosshair: Aiming reticle
- Enemy: Demon-like creatures
- Bullet: Projectile sprite
- Gun: Player weapon at bottom of screen
- Border: Play area boundary
- Game Over: End game text

### Game Loop
1. Process user inputs (keyboard)
2. Update player position and rotation
3. Fire bullets if space pressed
4. Update bullet positions
5. Update enemy positions (AI moves toward player)
6. Check collisions (bullets vs enemies, enemies vs player)
7. Render all active sprites
8. Wait for next frame

## Running the Game

```bash
python doom.py
```

Make sure you have the Quantum Machines QUA framework installed and configured with the correct QOP IP address in the code.

## Implementation Notes

- Uses QUA program to run game logic on quantum control hardware
- Renders graphics through analog outputs as X/Y vector signals
- Input handled through IO values set from keyboard events
- Fixed-point math for game calculations
- Collision detection using distance formulas

## Future Enhancements

Possible improvements:
- Add different enemy types with varying speeds/health
- Implement health pickups
- Add walls/maze elements for navigation
- Multiple weapon types
- Score tracking and high scores
- More complex enemy AI (pathfinding, attacking patterns)
- True 3D perspective rendering (raycasting)
- Sound effects via additional outputs
- Boss battles
- Levels/stages progression

## Credits

Created following the pattern of existing OPXBOX games (Pong, Flappy Bird, Mario) using the Quantum Machines QUA framework for vector graphics rendering on oscilloscope displays.
