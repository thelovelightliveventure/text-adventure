from characters import NPC, mayor, blacksmith, farmer, guard, child

###################################
######### Map Rendering ###########
###################################

def render_map(location, explored):
    x, y = location
    print("\nMap:")
    for row in range(-1, 2):
        for col in range(-1, 2):
            pos = (x + col, y + row)
            if pos == tuple(location):
                print("[X]", end=" ")
            elif pos in explored:
                print("[ ]", end=" ")
            else:
                print(" . ", end=" ")
        print()
    print()

def get_command():
    return input("\nWhat do you want to do? ").strip().lower()

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
world_map[(5, 5)] = {"name": "Village Center", "features": ["Bell Tower", "Well"], "npcs": ["Villager"]}
world_map[(5, 6)] = {"name": "North Street", "npcs": [child]}
world_map[(5, 7)] = {"name": "Mayor's House", "features": ["Mayor's Map"], "npcs": [mayor]}
world_map[(4, 5)] = {"name": "West Street", "npcs": [blacksmith]}
world_map[(6, 5)] = {"name": "East Street", "npcs": [farmer]}
world_map[(5, 4)] = {"name": "South Street", "npcs": [guard]}


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