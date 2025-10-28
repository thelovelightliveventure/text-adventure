import json, base64, random

#############################
#### Saving player state ####
#############################

def generate_save_code(state):
    json_str = json.dumps(state)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded

def load_from_code(code):
    try:
        json_str = base64.b64decode(code.encode()).decode()
        state = json.loads(json_str)
        return state
    except Exception:
        print("Invalid save code.")
        return None

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

########################
### GOSSIP GENERATOR ###
########################

class GossipGenerator:
    def __init__(self):
        self.gossip_list = [
            "The mayor's been meeting with himself again: in the mirror room.",
            "The carpenter once built a door that refused to close—it's still waiting for 'the right person.'",
            "The guard captain once arrested himself for suspicious behavior.",
            "The library basement isn’t on the building plans.",
            "The town sign is repainted with a different color every morning.",
            "Every year, someone new moves to town, but no one remembers them moving in.",
            "The innkeeper's ledger has names of guests who never existed.",
            "Nobody knows who founded the town. Every record just says \"someone important.\"",
            "On Bread Day, every family bakes a loaf for good luck. The baker refuses to eat hers.",
            "Our town motto: Big enough to know everyone, small enough to lose someone.",
            "Our town was founded after \"The Great Forgetting\". No one remembers what was forgotten, though."
        ]

    def get_gossip(self):
        if not self.gossip_list:
            return "Everyone's quiet now. Guess there's no more gossip left to spread."
        gossip = random.choice(self.gossip_list)
        self.gossip_list.remove(gossip)
        return gossip

class NPC:
    def __init__(self, name, role, dialogue, quest=None):
        self.name = name
        self.role = role
        self.dialogue = dialogue
        self.quest = quest
        self.met = False

    def interact(self, player_state):
        npc_flags = player_state.setdefault("npc_flags", {})
        flags = npc_flags.setdefault(self.name, {"met": False, "quest_accepted": False})

        if not flags["met"]:
            print(f"{self.name} ({self.role}) greets you.")
            print(f"\"{self.dialogue}\"")
            flags["met"] = True
        else:
            print(f"{self.name} says: \"Back again, are you?\"")

        if self.quest and not flags["quest_accepted"]:
            print(f"{self.name} offers you a quest: {self.quest['title']}")
            accept = input("Do you accept the quest? (y/n): ").lower()
            if accept == "y":
                print(f"Quest accepted: {self.quest['title']}")
                player_state["active_quest"] = self.quest
                flags["quest_accepted"] = True
# Named NPCs with unique dialogue and quests
mayor = NPC(
    name="Mayor",
    role="Village Leader",
    dialogue="I founded this town after the Great Forgetting. We must protect its secrets.",
    quest={"id": "mayor_map", "title": "Find the Mayor's Lost Map"}
)

blacksmith = NPC(
    name="Blacksmith",
    role="Craftsman",
    dialogue="My hammer once broke a cursed sword. I need rare ore to forge a new one.",
    quest={"id": "blacksmith_ore", "title": "Retrieve the Forgotten Ore"}
)

farmer = NPC(
    name="Farmer",
    role="Crop Tender",
    dialogue="The soil is cursed. I need enchanted seeds to restore the fields.",
    quest={"id": "farmer_seeds", "title": "Find the Enchanted Seeds"}
)

guard = NPC(
    name="Guard",
    role="Forest Watch",
    dialogue="I patrol the forest edge every night. Something is watching us.",
    quest={"id": "guard_watch", "title": "Investigate the Forest Shadows"}
)

child = NPC(
    name="Child",
    role="Curious Kid",
    dialogue="I saw something glowing near the bell tower. It whispered my name.",
    quest={"id": "child_glow", "title": "Find the Glowing Whisper"}
)

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