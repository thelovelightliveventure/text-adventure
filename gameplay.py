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
    engage_combat
)
import random, curses
import sys

def main(stdscr, initial_save_code=None):
    curses.curs_set(0) # Hide cursor

    # For debugging ------
    stdscr.addstr(0, 0, "Game is starting...")
    stdscr.refresh()
    curses.napms(1000)
    # End debugging ------

    stdscr.clear()
    stdscr.refresh()

    # Initialize windows (keep them within screen bounds)
    height, width = stdscr.getmaxyx()
    # desired input area height
    input_h = 9
    # make sure there's room for top area
    if input_h >= height - 3:
        input_h = max(3, height // 4)
    top_h = height - input_h

    left_w = width // 2
    right_w = width - left_w
    map_win = curses.newwin(top_h, left_w, 0, 0)
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
        "npc_flags": {}     # e.g., {"Blacksmith": {"met": True, "quest_accepted": True}}
    }

    # Initialize player_state from provided save code (if any)
    if initial_save_code:
        player_state = load_from_code(initial_save_code) or default_state
    else:
        player_state = default_state

    # Create gossip generator
    gossip_gen = GossipGenerator()

    while True:
        if player_state.get("health", 100) <= 0:
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "You collapse from your wounds...")
            input_win.addstr(2, 2, "You awaken in the Infirmary, patched up but shaken.")
            input_win.refresh()
            curses.napms(2000)
            player_state["location"] = [5, 3]
            player_state["health"] = 100

        render_map(map_win, player_state)
        render_info(info_win, player_state)
        command = get_command(input_win)

        if command in ["north", "south", "east", "west"]:
            (x, y) = player_state["location"]
            current_tile = world_map.get((x, y), {})
            doors = current_tile.get("doors", [])
        
            if command in doors:
                if command == "north": y -= 1
                elif command == "south": y += 1
                elif command == "east": x += 1
                elif command == "west": x -= 1
                player_state["location"] = [x, y]
                if (x, y) not in player_state["explored"]:
                    player_state["explored"].append((x, y))
            else:
                input_win.clear()
                input_win.box()
                input_win.addstr(1, 2, f"You can't go {command} from here.")
                input_win.refresh()
                input_win.getch()

            # Random encounter in the forest
            tile = world_map.get((x, y), {})
            if tile.get("name") == "Forest":
                if random.random() < 0.4:
                    creature = random.choice(forest_creatures)
                    engage_combat(input_win, player_state, creature)

        elif command == "inventory":
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, f"Inventory: {', '.join(player_state['inventory'])}")
            input_win.refresh()
            input_win.getch()

        elif command == "save":
            code = generate_save_code(player_state)
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Your save code:")
            input_win.addstr(2, 2, code)
            input_win.refresh()
            input_win.getch()

        elif command == "quit":
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Thanks for playing!")
            input_win.refresh()
            curses.napms(1500)
            break

        elif command == "help":
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Commands: north, south, east, west, inventory, save, help, quit")
            input_win.refresh()
            input_win.getch()

        elif command == "status":
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, f"Health: {player_state.get('health', 100)}")
            input_win.addstr(2, 2, f"Food: {player_state.get('food', 0)}")
            input_win.addstr(3, 2, f"Inventory: {', '.join(player_state['inventory'])}")
            input_win.refresh()
            input_win.getch()

        else:
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Unknown command.")
            input_win.addstr(2, 2, "Try: north, south, east, west, inventory, save, help, quit")
            input_win.refresh()
            input_win.getch()

    ###################### END GAME LOOP ##################################
    
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
    except Exception:
        with open("c:\\Users\\7tujo\\Programming\\text-adventure\\curses_error.log", "w", encoding="utf-8") as f:
            f.write("Unhandled exception in curses UI:\n\n")
            traceback.print_exc(file=f)
        print("Curses UI crashed — see curses_error.log for details.")