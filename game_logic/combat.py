# This file contains combat functions for handling battle sequences.
import curses
import random

def run_combat_sequence(win, player_state, creature, creature_first=False):
    player_health = player_state.get("health", 100)
    creature_health = creature.health

    if creature_first:
        player_health -= creature.damage
        win.clear()
        win.box()
        win.addstr(1, 2, f"The {creature.name} strikes first! You -{creature.damage} HP ({max(player_health, 0)}/100)")
        win.addstr(3, 2, "Press Enter to continue...")
        win.refresh()
        win.getch()

    while player_health > 0 and creature_health > 0:
        win.clear()
        win.box()
        # Player attacks
        creature_health -= creature.damage
        win.addstr(1, 2, f"You strike! {creature.name} -{creature.damage} HP ({max(creature_health, 0)}/{creature.health})")

        # If creature is dead then stop
        if creature_health <= 0:
            break

        # Creature attacks
        player_health -= creature.damage
        win.addstr(2, 2, f"{creature.name} lunges! You -{creature.damage} HP ({max(player_health, 0)}/100)")
        win.addstr(4, 2, "Press Enter to continue...")
        win.refresh()
        win.getch()

    if player_health <= 0:
        win.clear()
        win.box()
        win.addstr(1, 2, "You collapse from your wounds...")
        win.addstr(2, 2, "You awaken in the Infirmary, patched up but shaken.")
        player_state["location"] = [5, 3]
        player_health = 100
        win.refresh()
        curses.napms(2000)

    else:
        win.clear()
        win.box()
        win.addstr(1, 2, f"✅ You defeated the {creature.name}!")
        win.addstr(2, 2, f"You collect {creature.food_reward} food and some meat.")
        player_state["inventory"].append(f"{creature.name} meat")
        player_state["food"] = player_state.get("food", 0) + creature.food_reward
        player_state.setdefault("flags", {})[f"{creature.name.lower()}_attacked"] = True
        win.refresh()
        win.getch()

    player_state["health"] = player_health


def engage_combat(win, player_state, creature):
    hostile = creature.is_hostile(player_state)
    auto_attack = hostile and random.random() < getattr(creature, "attack_probability", 0.3)

    win.clear()
    win.box()
    win.addstr(1, 2, f"You encounter a {creature.name}!")
    win.addstr(2, 2, f"The {creature.name} looks {'hostile' if hostile else 'peaceful'}.")

    if auto_attack:
        win.addstr(4, 2, f"The {creature.name} lunges at you before you can react!")
        win.addstr(5, 2, "Press Enter to defend yourself...")
        win.refresh()
        win.getch()
        run_combat_sequence(win, player_state, creature, creature_first=True)
        return

    win.addstr(3, 2, "Do you want to [fight], [flee], or [observe]? ")
    win.refresh()

    curses.echo()
    action = win.getstr(4, 2).decode("utf-8").strip().lower()
    curses.noecho()

    if action == "fight":
        run_combat_sequence(win, player_state, creature)
    elif action == "flee":
        win.clear()
        win.box()
        win.addstr(1, 2, "You flee successfully, but your heart is pounding.")
        win.refresh()
        win.getch()
    elif action == "observe":
        win.clear()
        win.box()
        win.addstr(1, 2, f"You watch the {creature.name}. It does not react.")
        win.refresh()
        win.getch()
    else:
        win.clear()
        win.box()
        win.addstr(1, 2, "You hesitate. The moment passes.")
        win.refresh()
        win.getch()