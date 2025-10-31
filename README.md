# Welcome!
Welcome to my text adventure game! This is a game that's in progress. Thank you for your patience as I work things out!

# How to run
I've personally only tested this game in Windows Terminal (CMD). To run in Windows Terminal:

1. Open Windows Terminal (Win + R, "cmd", Enter)
2. Navigate to the folder in which ```gameplay.py``` is located.
3. Run ```python gameplay.py``` and have fun!

Notes: 
- This game cannot be run through VS Code terminal because it uses ```curses```.
- Python 3.11 is the recommended Python version.

# Files
```
.
├── gameplay.py
└── game_logic/
    ├── __init__.py
    ├── characters.py
    ├── world.py
    ├── combat.py    
    └── persistence.py
```
### ```gameplay.py```
This file handles the game's high-level flow, such as presenting information to the player and processing their commands.

### ```game_logic/```
This folder contains all the files for game logistics, functions, and classes.

### ```__init__.py```
This (often empty) file marks the ```game_logic``` directory as a package that Python can import.

### ```characters.py```
This file contains the ```Character``` class and any functions specifically related to character management.

### ```world.py```
This file holds ```Room``` and ```Location``` classes, along with functions for managing the game map.

### ```combat.py```
This file contains a ```CombatSystem``` class or functions for handling battle sequences.

### ```persistence.py```
This file contains functions specifically related to user saves and persistence management.