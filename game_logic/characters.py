# This file contains Character class and any functions related to character management.

import random

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

def render_char(win, player_state, named_npcs, gossip_gen):
    win.clear()
    win.box()
    win.addstr(1, 2, "Characters in Town:")
    y = 2
    for npc_key, npc in named_npcs.items():
        if npc.met:
            win.addstr(y, 4, f"- {npc.name} ({npc.role})")
            y += 1
    win.addstr(y + 1, 2, "Gossip:")
    gossip = gossip_gen.get_gossip()
    win.addstr(y + 2, 4, f"\"{gossip}\"")
    win.refresh()

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

named_npcs = {
    "mayor": mayor,
    "blacksmith": blacksmith,
    "farmer": farmer,
    "guard": guard,
    "child": child
}