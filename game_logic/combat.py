# This file contains a CombatSystem class or functions for handling battle sequences.
import time

# Color words in the console
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

def engage_combat(player_state, creature):
    print(f"\nYou encounter a {creature.name}!")

    hostile = creature.is_hostile(player_state)
    if hostile:
        print(f"The {creature.name} looks hostile!")
    else:
        print(f"The {creature.name} looks peaceful.")

    action = input("Do you want to [fight], [flee], or [observe]? ").lower()

    if action == "fight":
        print(f"⚔️  You fight the {creature.name}!")
        time.sleep(0.8)
        player_health = player_state.get("health", 100)
        creature_health = creature.health

        while player_health > 0 and creature_health > 0:
            # Player attacks
            creature_health -= creature.damage ### EVENTUALLY CHANGE THIS TO YOUR + WEAPON DAMAGE
            print(f"You strike! {creature.name} -{creature.damage} HP ({CYAN}{max(creature_health, 0)}{RESET}/{creature.health})") ### EVENTUALLY CHANGE THE /100 TO /ORIGINAL_HEALTH of CREATURE
            time.sleep(0.3)            

            # Creature attacks
            player_health -= creature.damage 
            print(f"{RED}{creature.name} lunges!{RESET} You {RED}-{creature.damage} {RESET}HP ({CYAN}{max(player_health, 0)}{RESET}/100)")
            time.sleep(0.3)
    elif action == "flee":
        print("You flee successfully, but your heart is pounding.")
    elif action == "observe":
        print(f"You watch the {creature.name}. It does not react.")
    else: 
        print("You hesitate. The moment passes.")