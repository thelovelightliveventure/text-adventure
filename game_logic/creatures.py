class Creature:
    def __init__(self, name, behavior, damage, food_reward, health=100, hostility_check=None, creature_description=None):
        self.name = name
        self.behavior = behavior # "passive", "aggressive", "conditional", etc
        self.damage = damage
        self.food_reward = food_reward
        self.health = health
        self.hostility_check = hostility_check
        self.creature_description = creature_description or f"A {name.lower()} is nearby."

    def is_hostile(self, player_state):
        if self.behavior == "aggressive":
            return True
        elif self.behavior == "passive":
            return False
        elif self.behavior == "conditional" and self.hostility_check:
            return self.hostility_check(player_state)
        return False

def boar_hostility(player_state):
    return "boar_attacked" in player_state.get("flags", {})

wild_boar = Creature("Wild Boar", "conditional", damage = 10, food_reward = 40, health = 40, hostility_check = boar_hostility, creature_description="A wild boar sniffs the ground nearby, tusks gleaming.")
deer = Creature("Deer", "passive", damage = 5, food_reward = 15, health = 30, creature_description="A deer is grazing peacefully nearby.")
wolf = Creature("Wolf", "aggressive", damage = 15, food_reward = 10, health = 75, creature_description="A wolf prowls through the shadows, watching you intently.")

forest_creatures = [wild_boar, deer, wolf]