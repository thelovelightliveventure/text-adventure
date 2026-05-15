import json
import random
from pathlib import Path

CREATURES_DATA_FILE = Path(__file__).parent / "creatures.json"

class Creature:
    def __init__(self, creature_id, name, behavior, damage, food_reward, health=100, 
                 description="", spawn_location=None, hostility=False, hostility_flag=None,
                 spawn_probability=0.7, attack_probability=0.3):
        self.id = creature_id
        self.name = name
        self.behavior = behavior  # "passive", "aggressive", "conditional", etc
        self.damage = damage
        self.food_reward = food_reward
        self.health = health
        self.creature_description = description or f"A {name.lower()} is nearby."
        self.spawn_location = spawn_location or [0, 0]
        self.current_location = list(spawn_location) if spawn_location else [0, 0]
        self.hostility = hostility
        self.hostility_flag = hostility_flag
        self.spawn_probability = spawn_probability
        self.attack_probability = attack_probability

    def is_hostile(self, player_state):
        if self.hostility:
            return True
        if self.behavior == "aggressive":
            return True
        elif self.behavior == "passive":
            return False
        elif self.behavior == "conditional" and self.hostility_flag:
            return self.hostility_flag in player_state.get("flags", {})
        return False

    def wander(self):
        """Move creature one square randomly"""
        direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.current_location[0] = max(0, min(9, self.current_location[0] + direction[0]))
        self.current_location[1] = max(0, min(9, self.current_location[1] + direction[1]))


def load_creatures_from_json():
    """Load and initialize creatures from JSON file"""
    creatures = {}
    
    if not CREATURES_DATA_FILE.exists():
        return creatures
    
    try:
        with open(CREATURES_DATA_FILE, 'r') as f:
            data = json.load(f)
        
        for creature_data in data.get("creatures", []):
            creature = Creature(
                creature_id=creature_data.get("id", ""),
                name=creature_data.get("name", "Unknown"),
                behavior=creature_data.get("behavior", "passive"),
                damage=creature_data.get("damage", 5),
                food_reward=creature_data.get("food_reward", 10),
                health=creature_data.get("health", 30),
                description=creature_data.get("description", ""),
                spawn_location=creature_data.get("spawn_location", [0, 0]),
                hostility=creature_data.get("hostile", False),
                hostility_flag=creature_data.get("hostility_flag", None),
                spawn_probability=creature_data.get("spawn_probability", 0.7),
                attack_probability=creature_data.get("attack_probability", 0.3)
            )
            creatures[creature.id] = creature
    except Exception as e:
        print(f"Error loading creatures from JSON: {e}")
    
    return creatures


def initialize_creatures(player_state):
    """Spawn creatures on game load based on spawn probability"""
    all_creatures = load_creatures_from_json()
    spawned_creatures = {}
    
    for creature_id, creature in all_creatures.items():
        # Use the spawn probability defined in the JSON
        if random.random() < creature.spawn_probability:
            spawned_creatures[creature_id] = creature
    
    player_state["creatures"] = spawned_creatures
    return spawned_creatures


def update_creatures(player_state):
    """Update creature positions (wandering) each turn"""
    creatures = player_state.get("creatures", {})
    for creature_id, creature in creatures.items():
        creature.wander()


# Load all creatures from JSON on module import
forest_creatures = load_creatures_from_json()
