FOREST - PYTHON PYGAME GAME
====================================

Forest is a dynamic 2D arcade game developed in Python using the Pygame library.  
The game places the player in a vibrant grid-based forest world, where quick thinking  
and fast movement are essential. The main goal is to collect all fruits scattered  
throughout the level while avoiding deadly enemies and strategically modifying the map  
by building or destroying obstacles in real time.

Enemies aren’t random - they use a simple **Breadth-First Search (BFS)** pathfinding algorithm  
to chase the player, introducing an additional layer of strategy and pressure.  
Levels are time-limited (60 seconds), and the player’s best completion times are recorded and  
displayed for each level.

Gameplay Overview
-----------------
- Move your character using arrow keys.
- Press SPACE to build or destroy obstacles in the direction you're facing.
- Collect all fruits on the level to win.
- Avoid enemies - one touch ends the game.
- You have 60 seconds to complete each level.
- The best completion time for each level is saved and displayed in a scoreboard.

Features
--------
- Smooth grid-based movement for player and movable fruits.
- Animated sprites and particle effects.
- Real-time block building and destruction.
- Enemy movement and interaction.
- Time tracking and best-score saving.
- Modular code structure for easy maintenance and expansion.


How to Run
----------
1. Make sure Python 3.10+ is installed.
2. Install the required libraries:
```bash
   pip install -r requirements.txt
 ```
3. Run the game:
```bash
   python Main.py
```

Notes
-----
Custom fonts and assets must be in the appropriate folders.

License
-------
This project is licensed under the MIT License