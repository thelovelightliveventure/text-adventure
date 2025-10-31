from game_logic import (
    GossipGenerator, 
    named_npcs, 
    load_from_code, 
    generate_save_code, 
    render_map, 
    render_info,
    get_command,
    world_map, 
    forest_creatures,
    engage_combat,
    food,
    render_char,
    normalize_direction
)
import random, curses
import sys

def main(stdscr, initial_save_code=None):
    curses.curs_set(0) # Hide cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # Heath
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Hunger

    # For debugging ------
    stdscr.addstr(0, 0, "Game is starting...")
    stdscr.refresh()
    curses.napms(1000)
    # End debugging ------

    stdscr.clear()
    stdscr.refresh()

  # Initialize windows (keep them within screen bounds)
    height, width = stdscr.getmaxyx()
    input_h = 9
    if input_h >= height - 3:
        input_h = max(3, height // 4)
    top_h = height - input_h

    left_w = width // 2
    right_w = width - left_w

    # split left area vertically: top = map, bottom = characters list
    left_top_h = max(3, top_h // 2)
    left_bottom_h = top_h - left_top_h

    map_win = curses.newwin(left_top_h, left_w, 0, 0)
    char_win = curses.newwin(left_bottom_h, left_w, left_top_h, 0)
    info_win = curses.newwin(top_h, right_w, 0, left_w)
    input_win = curses.newwin(input_h, width, top_h, 0)

    ############### GAME LOOP #################
    # Default starting state
    default_state = {
        "name": "User1",
        "role": "Explorer",
        "location": [5, 5],
        "inventory": ["backpack", "map", "useless dagger"],
        "quests_completed": [],
        "explored": [(0, 0)],
        "status_effects": [],  # list of active effect names, e.g. ["Poisoned"]
        "food": 100,
        "health": 100,
        "npc_flags": {}     # e.g., {"Blacksmith": {"met": True, "quest_accepted": True}}
    }

    # Initialize player_state from provided save code (if any)
    if initial_save_code:
        player_state = load_from_code(initial_save_code) or default_state
    else:
        player_state = default_state

    # Ensure starting position is marked explored so player marker shows immediately
    start_loc = tuple(player_state.get("location", [0, 0]))
    if start_loc not in player_state.get("explored", []):
        player_state.setdefault("explored", []).append(start_loc)

    # Create gossip generator
    gossip_gen = GossipGenerator()

    # Helper to show a brief message without forcing an extra keypress.
    # Use wait_ms to control how long the message stays visible (milliseconds).
    def show_msg(win, lines, wait_ms=1200):
        win.clear()
        win.box()
        for i, ln in enumerate(lines, start=1):
            try:
                win.addstr(i, 2, ln)
            except curses.error:
                # ignore if window too small
                pass
        win.refresh()
        curses.napms(wait_ms)

    # Find the first food in inventory that matches the templates.
    # Returns (index, inventory_name, template) or (None, None, None).
    def find_food(inventory):
        for i, item in enumerate(inventory):
            lname = item.lower()
            for template in food:
                if any(tok in lname for tok in template["match"]):
                    return i, item, template
        return None, None, None

    while True:
        # If dead, move to infirmary and enter resting mode (health regenerates incrementally).
        if player_state.get("health", 100) <= 0 and not player_state.get("resting"):
            show_msg(input_win, ["You collapse from your wounds...", "You awaken in the Infirmary."], wait_ms=1600)
            player_state["location"] = [5, 3]
            # keep the player barely alive and set resting state
            player_state["health"] = max(1, player_state.get("health", 0))
            player_state["resting"] = True
            player_state.setdefault("rest_regen", 6)  # HP regained per loop while resting

        render_map(map_win, player_state)
        render_char(char_win, player_state, named_npcs, gossip_gen)
        render_info(info_win, player_state)

        # If the player is resting, only allow 'stand' command (health increments each loop).
        if player_state.get("resting"):
            # Regen HP (capped to 100)
            regen = player_state.get("rest_regen", 5)
            old_hp = player_state.get("health", 0)
            player_state["health"] = min(100, old_hp + regen)
            gained = player_state["health"] - old_hp
            show_msg(input_win, [f"Resting... +{gained} HP", "Type 'stand' to stand."], wait_ms=800)

            # Clear input window to remove any stray characters before reading input.
            input_win.clear()
            input_win.box()
            input_win.refresh()
            command = get_command(input_win)
            if not command:
                continue
            command = command.strip()
            # Ignore single stray punctuation like "!" or other non-alphanumeric single chars
            if len(command) == 1 and not command.isalnum():
                continue
            command = command.lower()
            if command == "stand":
                player_state["resting"] = False
                show_msg(input_win, ["You stand up, ready to continue."], wait_ms=900)
            else:
                show_msg(input_win, ["You are resting. Type 'stand' to stand."], wait_ms=900)
            continue

        # Clear input window before prompting so leftover characters (like a stray "!")
        # don't remain visible and don't confuse get_command.
        input_win.clear()
        input_win.box()
        input_win.refresh()
        command = get_command(input_win)
        # sanitize command input: ignore empty or stray single-punctuation inputs and normalize
        if not command:
            continue
        command = command.strip()
        # ignore single non-alphanumeric characters (covers stray "!" etc.)
        if len(command) == 1 and not command.isalnum():
            continue

        command = normalize_direction(command) or command
        
        if command in ["north", "south", "east", "west"]:
            (x, y) = player_state["location"]
            current_tile = world_map.get((x, y), {})
            # If a tile defines "doors" it restricts allowed exits.
            # If "doors" is absent (outdoor/open tiles), allow movement freely.
            doors = current_tile.get("doors", None)
            if (doors is None) or (command in doors):
                if command == "north": y -= 1
                elif command == "south": y += 1
                elif command == "east": x += 1
                elif command == "west": x -= 1
                player_state["location"] = [x, y]
                if (x, y) not in player_state["explored"]:
                    player_state["explored"].append((x, y))
            else:
                show_msg(input_win, [f"You can't go {command} from here."], wait_ms=900)
                
            # Random encounter in the forest
            tile = world_map.get((x, y), {})
            if tile.get("name") == "Forest":
                # Random being encountered event
                if random.random() < 0.4:
                    creature = random.choice(forest_creatures)
                    # skip invalid creature entries (guard against None or malformed entries)
                    if not creature or (isinstance(creature, dict) and not creature.get("name")):
                        # no creature spawned — safe skip
                        continue

                    combat_result = engage_combat(input_win, player_state, creature)
                    # Decide if the player was bitten:
                    bitten = False
                    if isinstance(combat_result, dict):
                        # if engage_combat returns structured info, respect it
                        bitten = combat_result.get("player_bitten", False)
                    else:
                        # unknown return: fall back to a small random chance
                        if random.random() < 0.1:
                            bitten = True

                    if bitten:
                        show_msg(input_win, [
                            "The creature bites you!",
                            "You feel a burning sensation... You're poisoned!"
                        ], wait_ms=1400)
                        player_state.setdefault("status_effects", []).append("Poisoned")

        elif command == "inventory":
            show_msg(input_win, [f"Inventory: {', '.join(player_state.get('inventory', []))}"], wait_ms=1400)


        elif command == "eat":
            # Use the consumable templates above to find and apply an item.
            idx, item_name, template = find_food(player_state.get("inventory", []))
            if idx is not None:
                # remove item
                player_state["inventory"].pop(idx)
                # apply effects
                gain_food = template.get("food", 0)
                # If the template specifies hp, use it; otherwise give a small hp gain
                if "hp" in template:
                    gain_hp = template.get("hp", 0)
                else:
                    gain_hp = max(1, gain_food // 5)
                effect = template.get("effect")
                printEffect = f"and are now {effect}"
                player_state["food"] = player_state.get("food", 0) + gain_food
                # apply hp but cap at 100
                player_state["health"] = min(100, player_state.get("health", 100) + gain_hp)
                if effect:
                    # simple behavior: add the effect name; you can extend this to track durations
                    player_state.setdefault("status_effects", []).append(effect)
                show_msg(input_win, [f"You eat the {item_name}{printEffect}. (+{gain_food} food{', ' + str(gain_hp) + ' hp' if gain_hp else ''})"], wait_ms=1300)
            else:
                show_msg(input_win, ["You have nothing edible."], wait_ms=1000)

        elif command == "home":
            player_state["location"] = [5, 5]
            show_msg(input_win, ["You return to the Village Center."], wait_ms=900)

        elif command == "cure":
            effects = player_state.get("status_effects", [])
            if "Poisoned" in effects:
                player_state["status_effects"].remove("Poisoned")
                show_msg(input_win, ["You take a tonic and feel the poison fade."], wait_ms=1200)
            else:
                show_msg(input_win, ["You're not poisoned."], wait_ms=900)

        elif command == "save":
            code = generate_save_code(player_state)
            show_msg(input_win, ["Your save code:", code], wait_ms=2800)

        elif command == "quit":
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Thanks for playing!")
            input_win.refresh()
            curses.napms(1500)
            break

        elif command == "help":
            show_msg(input_win, ["Commands: north, south, east, west, inventory, save, help, quit"], wait_ms=1500)

        elif command == "status":
            effects = player_state.get("status_effects", [])
            if effects:
                show_msg(input_win, [f"Status Effects: {', '.join(effects)}"], wait_ms=1400)
            else:
                show_msg(input_win, ["You're feeling fine."], wait_ms=900)
        else:
            show_msg(input_win, [
                f"Unknown command: {command}",
                "Try: north, south, east, west, inventory, save, help, quit"
            ], wait_ms=1200)
#
# ...existing code...
    
if __name__ == "__main__":
    try:
        choice = input("Do you want to enter a save code to continue? (y/n): ").lower()
        if choice == "y":
            code = input("Paste your save code: ")
            initial_save_code = code
        else:
            initial_save_code = None
    except Exception:
        initial_save_code = None

    import traceback
    try:
        curses.wrapper(lambda stdscr: main(stdscr, initial_save_code))
    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write("Unhandled exception in curses UI:\n\n")
            traceback.print_exc(file=f)
        print("Curses UI crashed — see curses_error.log for details.")
        print("Error:", e)