# Welcome!
Welcome to my text adventure game!

# Files
```
.
├── gameplay.py
└── game_logic/
    ├── __init__.py
    ├── characters.py
    ├── world.py
    └── combat.py
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
