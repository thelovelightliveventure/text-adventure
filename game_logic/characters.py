# This file contains Character class and any functions related to character management.

import json
import random
from pathlib import Path

NPC_DATA_FILE = Path(__file__).parent / "npcs.json"

npc_definitions = {}

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

def _create_npc_from_spec(key, spec):
    return NPC(
        name=spec.get("name", key.title()),
        role=spec.get("role", "Wanderer"),
        dialogue=spec.get("dialogue", "Hello."),
        quest=spec.get("quest"),
        conversation=spec.get("conversation")
    )


def _default_npc_definitions():
    return {
        "mayor": {
            "name": "Mayor",
            "role": "Village Leader",
            "dialogue": "I founded this town after the Great Forgetting. We must protect its secrets.",
            "quest": {"id": "mayor_map", "title": "Mayor's Lost Map"}
        },
        "blacksmith": {
            "name": "Blacksmith",
            "role": "Craftsman",
            "dialogue": "My hammer once broke a cursed sword. I need rare ore to forge a new one.",
            "quest": {"id": "blacksmith_ore", "title": "Retrieve the Forgotten Ore"}
        },
        "farmer": {
            "name": "Farmer",
            "role": "Crop Tender",
            "dialogue": "The soil is cursed. I need enchanted seeds to restore the fields.",
            "quest": {"id": "farmer_seeds", "title": "Find the Enchanted Seeds"}
        },
        "guard": {
            "name": "Guard",
            "role": "Forest Watch",
            "dialogue": "I patrol the forest edge every night. Something is watching us.",
            "quest": {"id": "guard_watch", "title": "Investigate the Forest Shadows"}
        },
        "child": {
            "name": "Child",
            "role": "Curious Kid",
            "dialogue": "I saw something glowing near the bell tower. It whispered my name.",
            "quest": {"id": "child_glow", "title": "Find the Glowing Whisper"}
        }
    }


def _save_npc_definitions():
    global npc_definitions
    with NPC_DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(npc_definitions, f, indent=2, ensure_ascii=False)


def load_npcs():
    global npc_definitions
    if NPC_DATA_FILE.exists():
        try:
            with NPC_DATA_FILE.open("r", encoding="utf-8") as f:
                npc_definitions = json.load(f)
        except Exception:
            npc_definitions = _default_npc_definitions()
            _save_npc_definitions()
    else:
        npc_definitions = _default_npc_definitions()
        _save_npc_definitions()

    return {key: _create_npc_from_spec(key, spec) for key, spec in npc_definitions.items()}


def save_npcs():
    _save_npc_definitions()


def get_npc_definition(key):
    return npc_definitions.get(key)


def update_npc_definition(key, updates):
    global npc_definitions
    if key not in npc_definitions:
        return False
    npc_definitions[key].update(updates)
    old_npc = named_npcs.get(key)
    new_npc = _create_npc_from_spec(key, npc_definitions[key])
    if old_npc:
        new_npc.met = old_npc.met
    named_npcs[key] = new_npc
    _save_npc_definitions()
    return True


def create_npc_definition(key, data):
    global npc_definitions
    if key in npc_definitions:
        return False
    npc_definitions[key] = data
    named_npcs[key] = _create_npc_from_spec(key, data)
    _save_npc_definitions()
    return True


def delete_npc_definition(key):
    global npc_definitions
    if key not in npc_definitions:
        return False
    del npc_definitions[key]
    named_npcs.pop(key, None)
    _save_npc_definitions()
    return True


def render_char(win, player_state, named_npcs, gossip_gen, world_map):
    win.clear()
    win.box()
    win.addstr(1, 2, "Characters in Room:")
    y = 2
    loc = tuple(player_state.get("location", [0, 0]))
    tile = world_map.get(loc, {})
    room_npcs = [npc_key for npc_key in tile.get("npcs", []) if isinstance(npc_key, str)]
    if room_npcs:
        for npc_key in room_npcs:
            npc = named_npcs.get(npc_key)
            if npc:
                win.addstr(y, 4, f"- {npc.name} ({npc.role})")
            else:
                win.addstr(y, 4, f"- {npc_key}")
            y += 1
    else:
        win.addstr(y, 4, "(none)")
        y += 1
    win.addstr(y + 1, 2, "Gossip:")
    gossip = gossip_gen.get_gossip()
    win.addstr(y + 2, 4, f"\"{gossip}\"")
    win.refresh()

class NPC:
    def __init__(self, name, role, dialogue, quest=None, conversation=None):
        self.name = name
        self.role = role
        self.dialogue = dialogue
        self.quest = quest
        self.conversation = conversation
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

named_npcs = load_npcs()
