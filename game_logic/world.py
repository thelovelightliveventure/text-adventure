from .characters import NPC, named_npcs
import curses
import json
from pathlib import Path

###################################
######### Map Rendering ###########
###################################

MAP_DATA_FILE = Path(__file__).parent / "map_data.json"


def load_world_map():
    """Load map tile definitions from JSON."""
    default_width = 10
    default_height = 10
    default_tile = {
        "name": "Forest",
        "description": "You walk into a dense forest with towering trees. Sunlight filters through the canopy."
    }
    world_map = {}

    if not MAP_DATA_FILE.exists():
        for x in range(default_width):
            for y in range(default_height):
                world_map[(x, y)] = default_tile.copy()
        return world_map

    try:
        with open(MAP_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        size = data.get("size", [default_width, default_height])
        width, height = size[0], size[1]
        default_tile = data.get("default_tile", default_tile)

        for x in range(width):
            for y in range(height):
                world_map[(x, y)] = default_tile.copy()

        for zone in data.get("zones", []):
            tile = zone.get("tile", {})
            x1 = zone.get("x1", 0)
            y1 = zone.get("y1", 0)
            x2 = zone.get("x2", width - 1)
            y2 = zone.get("y2", height - 1)
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    if 0 <= x < width and 0 <= y < height:
                        world_map[(x, y)] = tile.copy()

        for special in data.get("special_tiles", []):
            x = special.get("x")
            y = special.get("y")
            tile = special.get("tile", {})
            if x is not None and y is not None:
                world_map[(x, y)] = tile.copy()

    except Exception as e:
        print(f"Error loading map data from JSON: {e}")
        for x in range(default_width):
            for y in range(default_height):
                world_map[(x, y)] = default_tile.copy()

    return world_map


world_map = load_world_map()


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

    # Use the window size to determine how many tiles can be drawn
    height, width = win.getmaxyx()
    tile_size = 3
    offset_y = 1
    offset_x = 2
    visible_w = max(3, min((width - offset_x - 1) // tile_size, 20))
    visible_h = max(3, min(height - offset_y - 4, 12))

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
    status_y = min(height - 2, offset_y + visible_h)
    try:
        win.addstr(status_y, 2, f"Location: {player_state['location']} — {room}")
    except curses.error:
        pass
    win.refresh()

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
            for npc_ref in data["npcs"]:
                if isinstance(npc_ref, str):
                    if npc_ref.lower() == "villager":
                        print(f"- Villager whispers: \"{gossip_gen.get_gossip()}\"")
                    else:
                        npc_key = npc_ref.lower()
                        npc = named_npcs.get(npc_key)
                        if npc:
                            npc.interact(player_state)
                        else:
                            print(f"- Unknown NPC reference: {npc_ref}")
    else:
        print("You are in an unremarkable part of the forest.")

def get_room_description(location, player_state):
    """
    Returns a list of description strings for a location.
    Includes the base room description only; creature descriptions are shown
    during actual combat encounters.
    """
    loc = tuple(location)
    tile = world_map.get(loc, {})
    description_lines = []
    
    # Add base room description
    if "description" in tile:
        description_lines.append(tile["description"])
    else:
        description_lines.append(f"You walk into {tile.get('name', 'an unknown place')}.")
    
    return description_lines

def normalize_direction(command):
    command = command.lower().strip()

    north_aliases = ["n", "go north", "move north", "up", "u", "key_up", "↑", "move up", "go up"]
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

