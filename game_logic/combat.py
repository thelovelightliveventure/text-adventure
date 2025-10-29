# This file contains a CombatSystem class or functions for handling battle sequences.

def engage_combat(player_state, creature):
    print(f"\nYou encounter a {creature.name}!")

    hostile = creature.is_hostile(player_state)
    if hostile:
        print(f"The {creature.name} looks hostile!")
    else:
        print(f"The {creature.name} looks peaceful.")

    action = input("Do you want to [fight], [flee], or [observe]? ").lower()

    if action == "fight":
        print(f"⚔️ You fight the {creature.name}!")
        player_health = player_state.get("health", 100)
        creature_health = creature.health

        while player_health > 0 and creature_health > 0:
            # Player attacks
            creature_health -= creature.damage ### EVENTUALLY CHANGE THIS TO YOUR + WEAPON DAMAGE
            print(f"You stab the {creature.name}! {creature.name} health -{creature.damage}, now {max(creature_health), 0}")

            # Creature attacks
            player_health -= creature.damage 
            print(f"{creature.name} attacks you! Your health -{creature.damage}, now {max(player_health, 0)}")
    elif action == "flee":
        print("You flee successfully, but your heart is pounding.")
    elif action == "observe":
        print(f"You watch the {creature.name}. It does not react.")
    else: 
        print("You hesitate. The moment passes.")