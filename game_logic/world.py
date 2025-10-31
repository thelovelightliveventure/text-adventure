from .characters import NPC, mayor, blacksmith, farmer, guard, child
import curses

###################################
######### Map Rendering ###########
###################################

def render_map(win, player_state):
    """
    Colored map render:
      - Forest tiles => green (color_pair 3)
      - Village tiles => yellow/brown (color_pair 4)
      - Village center => red (color_pair 5)
      - Unknown/default => color_pair 6 or normal
    Assumes color pairs are initialized by the caller (gameplay.py).
    """
    win.clear()
    win.box()

    explored = set(player_state.get("explored", []))
    px, py = player_state["location"]

    # Define visible window size
    visible_w = 11  # tiles across
    visible_h = 7   # tiles down
    tile_size = 3
    offset_y = 1
    offset_x = 2

    # Calculate top-left corner of visible map
    start_x = px - visible_w // 2
    start_y = py - visible_h // 2

    door_symbols = {
        "north": "↑",
        "south": "↓",
        "east": "→",
        "west": "←"
    }

    for dy in range(visible_h):
        for dx in range(visible_w):
            x = start_x + dx
            y = start_y + dy
            screen_y = offset_y + dy
            screen_x = offset_x + dx * tile_size

            tile = world_map.get((x, y), {})
            if (x, y) not in explored:
                try:
                    win.addstr(screen_y, screen_x, "   ")
                except curses.error:
                    pass
                continue

            name = (tile.get("name") or "").lower()
            # choose color pair based on tile type (gameplay.py should init these pairs)
            if curses.has_colors():
                if "forest" in name:
                    color = curses.color_pair(3)
                elif "village center" in name or "center" in name:
                    color = curses.color_pair(5)
                elif "village" in name:
                    color = curses.color_pair(4)
                else:
                    # default/unknown
                    color = curses.color_pair(6)
            else:
                color = 0

            doors = tile.get("doors", [])
            door_char = " "
            for d in ("north", "south", "east", "west"):
                if d in doors:
                    door_char = door_symbols.get(d, " ")
                    break

            try:
                if [x, y] == player_state["location"]:
                    # player marker highlighted
                    attr = curses.A_BOLD
                    if curses.has_colors():
                        attr |= curses.color_pair(7)
                    win.addstr(screen_y, screen_x, "[X]", attr)
                else:
                    # draw tile with chosen color
                    if door_char.strip():
                        win.addstr(screen_y, screen_x, f"[{door_char}]", color)
                    else:
                        win.addstr(screen_y, screen_x, "[ ]", color)
            except curses.error:
                pass

    loc = tuple(player_state["location"])
    room = world_map.get(loc, {}).get("name", "Unknown")
    try:
        win.addstr(visible_h + 2, 2, f"Location: {player_state['location']} — {room}")
    except curses.error:
        pass
    win.refresh()

#####################
##### WORLD MAP #####
#####################

# Generate a 10x10 grid with a village in the center
world_map = {}
for x in range(10):
    for y in range(10):
        if 3 <= x <= 6 and 3 <= y <= 6:
            # Village zone
            world_map[(x, y)] = {"name": "Village Outskirts"}
        else:
            world_map[(x, y)] = {"name": "Forest"}

# Add landmarks and NPCs
world_map[(5, 5)] = {
    "name": "Village Center", 
    "features": ["Bell Tower", "Well"], 
    "npcs": ["Villager"],
    "doors": ["north", "south", "east", "west"]
}
world_map[(5, 6)] = {
    "name": "North Street", 
    "npcs": [child],
    "doors": ["north", "south"]
}
world_map[(5, 7)] = {
    "name": "Mayor's House", 
    "features": ["Mayor's Map"], 
    "npcs": [mayor],
    "doors": ["south"]
}
world_map[(4, 5)] = {
    "name": "West Street", 
    "npcs": [blacksmith],
    "doors": ["east", "west"]
}
world_map[(6, 5)] = {
    "name": "East Street", 
    "npcs": [farmer],
    "doors": ["east", "west"]
}
world_map[(5, 4)] = {
    "name": "South Street", 
    "npcs": [guard],
    "doors": ["north", "south"]
}
world_map[(5, 3)] = {
    "name": "Infirmary", 
    "features": ["Bandages", "Herbal Tonic", "Quiet Beds"],
    "doors": ["north"]
}


# Location description function
def describe_location(location, gossip_gen, player_state):
    loc = tuple(location)
    if loc in world_map:
        data = world_map[loc]
        print(f"\nYou arrive at {data['name']}.")
        if "features" in data:
            print("You see:", ", ".join(data["features"]))
        if "npcs" in data:
            print("People nearby:")
            for npc in data["npcs"]:
                if isinstance(npc, str) and npc.lower() == "villager":
                    print(f"- Villager whispers: \"{gossip_gen.get_gossip()}\"")
                elif isinstance(npc, NPC):
                    npc.interact(player_state)
    else:
        print("You are in an unremarkable part of the forest.")

def normalize_direction(command):
    command = command.lower().strip()

    north_aliases = ["n", "go north", "move north", "up", "u", "w", "key_up", "↑", "move up", "go up"]
    south_aliases = ["s", "go south", "move south", "down", "d", "s", "key_down", "↓", "move down", "go down"]
    east_aliases = ["e", "go east", "move east", "right", "r", "d", "key_right", "→", "move right", "go right"]
    west_aliases = ["w", "go west", "move west", "left", "l", "a", "key_left", "←", "move left", "go left"]

    if command in north_aliases:
        return "north"
    elif command in south_aliases: 
        return "south"
    elif command in east_aliases:
        return "east"
    elif command in west_aliases:
        return "west"
    return None

