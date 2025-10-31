---------------------------------
-----------WHILE CODING----------
---------------------------------
Self-notes (notes for coding):
- Adapt to curses

To develop:
- CONSOLE: Make a help menu for commands and expand menu (kill, hunt, loot, examine, n\up=north etc)
- CHARACTERS: Make a way for NPCs with backstories to interact with users.
- COMBAT: add weapons and armor to reduce damage, add creature loot tables, add hunt
- CREATURES: make animals stay near where they spawned for consistency
- COMBAT: you start out with a somewhat useless dagger, determines your damage
- COMBAT: you die/respawn in the infirmary, and gradually get health
- COMBAT: make sure the color is different so combat looks cool in console
- CREATURES: more deer spawn than wolf, etc. also add new animals, and animals start with diff health
- make console easier to read (not so spaced apart, less line breaks)
- CONSOLE: kill will always try to find someone, otherwise "there is nothing nearby to kill"
- change cure and infirmary health bar effects
- the characters gossip overwrites boundary lines

Current bugs:
- Deer COMBAT never ends

---------------------------------
---------CODE PLANNING-----------
---------------------------------
General notes:
- use Python to create the game

Modular File Structure:
text_adventure/
├── gameplay.py         # Main game loop
├── helper.py           # Utility functions (e.g., map rendering, input parsing)
├── sidequests.py       # Optional side quest logic
├── characters.py       # Character classes and logic
├── quests.json         # Quest data
├── map.json            # World map


Concerns:
- Will user get lost? Map needed? If so, how?
- how to save user progress? save code/login?
- develop story


----------------------------------
----------STORY PLANNING----------
----------------------------------

CHARACTERS:
Innkeeper
    - He lives in THE INN. He's slippery and will make you overpay.
    - He runs the only inn in the town, and will always say "We're full." unless you flatter him.
    - SIDE QUEST: He's looking for a key.

Guard Captain - MacKaw MacOw:
    - Takes his job way too seriously for a town that has a zero crime rate.
    - Suspicious of everyone and also, hates explorers.
    - Constantly training new recruits that don't exist.
    - Secretly afraid of chickens.
    - SIDE QUEST: You'll get Guard points (he'll like you a little more) if you solve
        mysteries for him.

Gossipy neighbor - Mira Willow:
    - Knows everything, tells everyone.
    - Sells "fresh bread" along with fresh rumors.
    - Nobody knows how old she is, she seems to have been around forever...

Mayor:
    - Loud and overly cheerful.
    - Suspiciously defensive whenever someone mentions "the well incident."
    - Loves hosting "mandatory festivals"
    - Knows everyone's secrets (or thinks he does)
    - Has a map that shows a forest that doesn't exist anymore (there's a lake there)

The Blacksmith:
    - Says everything is "the best work I've ever done" even when it's clearly falling apart
    - Used to be an adventurer; doesn't talk about "the tunnels" anymore.

SIDE CHARACTERS:
The Mysterious Traveler - "The Stranger"
    - Keeps showing up in random places.
    - Never gives a real name.
    - Maybe helping you? Maybe spying on you?
    - PLOT: If you save him, he'll level up your sword.

The Herbalist:
    - Lives just outside town.
    - Sells potions that "probably work."
    - Talks to her plants more than people. One of them talks back.
    - SIDE QUEST: Find a rare herb for her. You'll get a life potion in return.

The Baker's Kid - Finn:
    - Always where he shouldn't be.
    - Knows all the shortcuts and hiding spots.
    - Claims to have seen "something glowing" in the forests beyond the town.

The Librarian - Miss Dovetail:
    - Sweet, ancient, and maybe immortal?
    - The library reorganizes itself after closing.
    - She insists books "choose their readers."
    - PLOT: if you correctly answer her book trivia questions, you'll get her 
    "book of ancient wisdom."

The Talking Crow:
    - Vastly annoying, delivers gossip
A "Guard Recruit":
    - Clearly a scarecrow in armor.
The Retired Adventurer Couple
    - They argue about whose fault the dragon incident was.
The Dog named "Mayor":
    - Half the town votes for it every election, you must treat it with respect.

CREATURES IN FOREST:
    - Wild boar that hates everyone, -10 health/attack, +40 food.
    - Deer that flit harmlessly by, +20 food.
    - Wolf that attacks everyone, -15 health/attack, +10 food.

LOCATIONS:


PLOTS, STORY, AND MORE:




SIDE QUESTS:
    - Who repaints the town sign every morning?
TOWN MYSTERIES:
    - The town sign is repainted with a different color every morning. Who and why?
    - Every year, someone new moves to town, but no one remembers them moving in.
    - The innkeeper's ledger has names of guests who never existed.
    - Nobody knows who founded the town. Every record just says "someone important."
    - Bread Day: Every family bakes a loaf for good luck. The baker refuses to eat hers.
    - Town motto: "Small enough to know everyone, big enough to lose someone."
    - Town was founded after "The Great Forgetting". No one remembers what was forgotten.

EASTER EGGS:

WORLDBUILDING:
    - VILLAGE
        - Old well in the center, sealed with iron chains (town ordinance #14)
    - FOREST
    - 
