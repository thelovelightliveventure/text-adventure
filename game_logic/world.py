from .characters import NPC, mayor, blacksmith, farmer, guard, child

###################################
######### Map Rendering ###########
###################################

def render_map(win, player_state):
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

    for dy in range(visible_h):
        for dx in range(visible_w):
            x = start_x + dx
            y = start_y + dy
            screen_y = offset_y + dy
            screen_x = offset_x + dx * tile_size

            tile = world_map.get((x, y), {})
            if (x, y) not in explored:
                win.addstr(screen_y, screen_x, "   ")  # blank space
                continue

            doors = tile.get("doors", [])
            door_symbols = {
                "north": "↑",
                "south": "↓",
                "east": "→",
                "west": "←"
            }
            door_str = "".join(door_symbols[d] for d in doors if d in door_symbols)

            if [x, y] == player_state["location"]:
                win.addstr(screen_y, screen_x, "[X]")
            elif door_str:
                win.addstr(screen_y, screen_x, f"[{door_str[0]}]")
            else:
                win.addstr(screen_y, screen_x, "[ ]")

    loc = tuple(player_state["location"])
    room = world_map.get(loc, {}).get("name", "Unknown")
    win.addstr(visible_h + 2, 2, f"Location: {player_state['location']} — {room}")
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