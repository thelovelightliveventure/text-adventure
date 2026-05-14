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
    normalize_direction,
    save_npcs,
    update_npc_definition,
    create_npc_definition,
    delete_npc_definition
)
import random, curses
import sys

ADMIN_PASSWORD = "admin123"

def main(stdscr, initial_save_code=None):
    curses.curs_set(0) # Hide cursor
    curses.start_color()
    # allow terminal default background (better on Windows)
    try:
        curses.use_default_colors()
    except Exception:
        pass
    # Basic UI pairs
    curses.init_pair(1, curses.COLOR_RED, -1)    # Health / emphasis
    curses.init_pair(2, curses.COLOR_YELLOW, -1) # Hunger / emphasis
    # Map color pairs (must match world.render_map usage)
    curses.init_pair(3, curses.COLOR_GREEN, -1)  # Forest
    curses.init_pair(4, curses.COLOR_YELLOW, -1) # Village / brownish
    curses.init_pair(5, curses.COLOR_RED, -1)    # Village center (strong red)
    curses.init_pair(6, curses.COLOR_WHITE, -1)  # Unknown / default
    curses.init_pair(7, curses.COLOR_CYAN, -1)   # Player highlight

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
        "npc_flags": {},     # e.g., {"Blacksmith": {"met": True, "quest_accepted": True}}
        "admin": False
    }

    # Initialize player_state from provided save code (if any)
    if initial_save_code:
        player_state = load_from_code(initial_save_code) or default_state
    else:
        player_state = default_state
    player_state.setdefault("admin", False)

    # Ensure starting position is marked explored so player marker shows immediately
    start_loc = tuple(player_state.get("location", [0, 0]))
    if start_loc not in player_state.get("explored", []):
        player_state.setdefault("explored", []).append(start_loc)

    # Create gossip generator
    gossip_gen = GossipGenerator()

    # Helper to show a brief message without forcing an extra keypress.
    # Use wait_ms to control how long the message stays visible (milliseconds).
    # If wait_for_key is True, wait for user to press any key instead.
    def show_msg(win, lines, wait_ms=1200, wait_for_key=False):
        win.clear()
        win.box()
        for i, ln in enumerate(lines, start=1):
            try:
                win.addstr(i, 2, ln)
            except curses.error:
                # ignore if window too small
                pass
        win.refresh()
        if wait_for_key:
            curses.noecho()
            win.getch()
            curses.noecho()
        else:
            curses.napms(wait_ms)

    def prompt_input(win, prompt, hide=False):
        win.clear()
        win.box()
        try:
            win.addstr(1, 2, prompt)
        except curses.error:
            pass
        win.refresh()
        if hide:
            curses.noecho()
        else:
            curses.echo()
        try:
            value = win.getstr(2, 2).decode("utf-8").strip()
        except Exception:
            value = ""
        finally:
            curses.noecho()
        return value

    # Admin commands menu
    def admin_help():
        input_win.clear()
        input_win.box()
        help_lines = [
            "Admin commands:",
            "admin login, admin logout, admin list npcs, admin list placements",
            "admin show npc <key>, admin edit npc <key>",
            "admin create npc <key>, admin remove npc <key>",
            "admin place npc <key> x y, admin unplace npc <key> x y",
            "Press any key to continue..."
        ]
        for i, ln in enumerate(help_lines, start=1):
            try:
                input_win.addstr(i, 2, ln)
            except curses.error:
                pass
        input_win.refresh()
        curses.noecho()
        input_win.getch()
        curses.noecho()

    def get_local_npc_keys():
        loc = tuple(player_state["location"])
        tile = world_map.get(loc, {})
        return [npc for npc in tile.get("npcs", []) if isinstance(npc, str)]

    def choose_option(prompt, options):
        max_rows = input_h - 4
        options = options[:max_rows]
        while True:
            input_win.clear()
            input_win.box()
            try:
                input_win.addstr(1, 2, prompt)
                for idx, option in enumerate(options, start=1):
                    input_win.addstr(1 + idx, 2, f"{idx}. {option}")
                input_win.addstr(2 + len(options), 2, "Choice: ")
            except curses.error:
                pass
            input_win.refresh()
            curses.echo()
            try:
                choice = input_win.getstr(3 + len(options), 2).decode("utf-8").strip()
            except Exception:
                choice = ""
            finally:
                curses.noecho()
            if not choice:
                return None
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return index
            show_msg(input_win, ["Invalid choice. Try again."], wait_ms=900)

    def run_npc_conversation(npc):
        npc_flags = player_state.setdefault("npc_flags", {})
        flags = npc_flags.setdefault(npc.name, {"met": False, "quest_accepted": False})
        # Special handling if quest accepted
        if flags.get("quest_accepted") and npc.quest:
            required_item = npc.quest.get("required_item")
            # Check for quest completion
            if required_item and required_item in player_state.get("inventory", []) and hasattr(npc, "quest_complete_conversation"):
                conversation = getattr(npc, "quest_complete_conversation")
            else:
                post_msg = getattr(npc, "post_quest_message", f"{npc.name}: You already have my quest. Go complete it!")
                show_msg(input_win, [post_msg], wait_for_key=True)
                return
        else:
            conversation = getattr(npc, "conversation", None)
        if conversation and isinstance(conversation, dict):
            node_key = "start"
            while node_key:
                node = conversation.get(node_key)
                if not node:
                    show_msg(input_win, ["This conversation branch is missing."], wait_ms=1200)
                    break
                # Unlock quest if node offers it
                if node.get("offers_quest"):
                    flags["quest_unlocked"] = True
                npc_lines = node.get("npc", [])
                if isinstance(npc_lines, str):
                    npc_lines = [npc_lines]
                for line in npc_lines:
                    show_msg(input_win, [f"{npc.name}: {line}"], wait_for_key=True)
                options = node.get("options", [])
                if not options:
                    break
                option_texts = [opt.get("text", "") for opt in options]
                selected = choose_option("Choose a reply:", option_texts)
                if selected is None:
                    break
                chosen_option = options[selected]
                action = chosen_option.get("action")
                if action == "accept_quest" and npc.quest and not flags.get("quest_accepted"):
                    player_state["active_quest"] = npc.quest
                    flags["quest_accepted"] = True
                    show_msg(input_win, [f"Quest accepted: {npc.quest['title']}"], wait_for_key=True)
                elif action == "complete_quest":
                    required_item = npc.quest.get("required_item")
                    reward_item = npc.quest.get("reward_item", "reward")
                    if required_item in player_state.get("inventory", []):
                        player_state["inventory"].remove(required_item)
                    player_state["inventory"].append(reward_item)
                    player_state.setdefault("quests_completed", []).append(npc.quest["id"])
                    if "active_quest" in player_state:
                        del player_state["active_quest"]
                    flags["quest_completed"] = True
                    show_msg(input_win, ["Quest completed!"], wait_for_key=True)
                next_key = chosen_option.get("next")
                if not next_key or next_key == "end":
                    break
                node_key = next_key
        else:
            if isinstance(npc.dialogue, list):
                for line in npc.dialogue:
                    show_msg(input_win, [f"{npc.name}: {line}"], wait_for_key=True)
            else:
                show_msg(input_win, [f"{npc.name}: {npc.dialogue}"], wait_for_key=True)
        flags["met"] = True
        # Quest prompt logic
        if npc.quest and not flags.get("quest_accepted"):
            if conversation:
                # For NPCs with conversation, only prompt if quest is unlocked
                if flags.get("quest_unlocked", False):
                    answer = prompt_input(input_win, f"Accept quest '{npc.quest['title']}'? (y/n): ")
                    if answer.lower() == "y":
                        player_state["active_quest"] = npc.quest
                        flags["quest_accepted"] = True
                        show_msg(input_win, [f"Quest accepted: {npc.quest['title']}"], wait_for_key=True)
                    else:
                        show_msg(input_win, ["Quest declined."], wait_for_key=True)
            else:
                # For NPCs without conversation, always prompt after dialogue
                answer = prompt_input(input_win, f"Accept quest '{npc.quest['title']}'? (y/n): ")
                if answer.lower() == "y":
                    player_state["active_quest"] = npc.quest
                    flags["quest_accepted"] = True
                    show_msg(input_win, [f"Quest accepted: {npc.quest['title']}"], wait_for_key=True)
                else:
                    show_msg(input_win, ["Quest declined."], wait_for_key=True)

    def talk_to_npc(key):
        loc_npcs = get_local_npc_keys()
        if key not in loc_npcs and key.lower() != "villager":
            show_msg(input_win, [f"{key} is not here."], wait_ms=1400)
            return
        if key.lower() == "villager":
            show_msg(input_win, [f"A villager whispers: \"{gossip_gen.get_gossip()}\""], wait_ms=1800)
            return
        npc = named_npcs.get(key)
        if not npc:
            show_msg(input_win, [f"No NPC with key: {key}"], wait_ms=1400)
            return
        run_npc_conversation(npc)

    def location_npc_list_text():
        keys = get_local_npc_keys()
        if keys:
            return ", ".join(keys)
        return "none"

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
        render_char(char_win, player_state, named_npcs, gossip_gen, world_map)
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
        
        # Admin command handling (must start with "admin")
        if command.startswith("admin"):
            tokens = command.split()
            if command == "admin" and player_state["admin"] == True:
                admin_help()
                continue

            if tokens == ["admin", "login"]:
                password = prompt_input(input_win, "Admin password: ", hide=True)
                if password == ADMIN_PASSWORD:
                    player_state["admin"] = True
                    show_msg(input_win, ["Admin mode enabled."], wait_ms=1200)
                else:
                    show_msg(input_win, ["Wrong admin password."], wait_ms=1200)
                continue

            if tokens == ["admin", "logout"]:
                player_state["admin"] = False
                show_msg(input_win, ["Admin mode disabled."], wait_ms=1200)
                continue

            if tokens == ["admin", "list", "npcs"]:
                keys = ", ".join(named_npcs.keys()) or "(none)"
                show_msg(input_win, ["NPC keys:", keys], wait_ms=2200)
                continue

            if tokens == ["admin", "list", "placements"]:
                placements = []
                for loc, tile in world_map.items():
                    for npc_ref in tile.get("npcs", []):
                        if isinstance(npc_ref, str):
                            placements.append(f"{npc_ref}@{loc}")
                if not placements:
                    show_msg(input_win, ["No NPCs placed on the map."], wait_ms=1400)
                else:
                    lines = ["NPC placements:"] + placements[:5]
                    if len(placements) > 5:
                        lines.append(f"...and {len(placements) - 5} more")
                    show_msg(input_win, lines, wait_ms=2600)
                continue

            if len(tokens) >= 4 and tokens[1] == "show" and tokens[2] == "npc":
                key = tokens[3]
                npc = named_npcs.get(key)
                if not npc:
                    show_msg(input_win, [f"No NPC with key: {key}"], wait_ms=1400)
                    continue
                quest_text = npc.quest["title"] if npc.quest else "None"
                conv_flag = "yes" if getattr(npc, "conversation", None) else "no"
                dialogue_text = npc.dialogue if isinstance(npc.dialogue, str) else "[list dialogue]"
                show_msg(input_win, [f"{npc.name} ({npc.role})", f"Dialogue: {dialogue_text}", f"Quest: {quest_text}", f"Has conversation: {conv_flag}"], wait_ms=3400)
                continue

            if len(tokens) >= 4 and tokens[1] == "edit" and tokens[2] == "npc":
                if not player_state.get("admin"):
                    show_msg(input_win, ["Admin required."], wait_ms=1200)
                    continue
                key = tokens[3]
                npc = named_npcs.get(key)
                if not npc:
                    show_msg(input_win, [f"No NPC with key: {key}"], wait_ms=1400)
                    continue
                field = prompt_input(input_win, "Field to edit (name/role/dialogue/quest/conversation): ")
                if field == "quest":
                    quest_id = prompt_input(input_win, "Quest id: ")
                    quest_title = prompt_input(input_win, "Quest title: ")
                    updated = update_npc_definition(key, {"quest": {"id": quest_id, "title": quest_title}})
                elif field == "conversation":
                    conv_json = prompt_input(input_win, "Enter conversation JSON: ")
                    try:
                        conversation = __import__("json").loads(conv_json)
                        updated = update_npc_definition(key, {"conversation": conversation})
                    except Exception:
                        updated = False
                else:
                    new_value = prompt_input(input_win, f"New {field}: ")
                    updated = update_npc_definition(key, {field: new_value})
                if updated:
                    show_msg(input_win, [f"NPC {key} updated."], wait_ms=1200)
                else:
                    show_msg(input_win, ["Failed to update NPC."], wait_ms=1200)
                continue

            if len(tokens) >= 4 and tokens[1] == "remove" and tokens[2] == "npc":
                if not player_state.get("admin"):
                    show_msg(input_win, ["Admin required."], wait_ms=1200)
                    continue
                key = tokens[3]
                if delete_npc_definition(key):
                    for tile in world_map.values():
                        if key in tile.get("npcs", []):
                            tile["npcs"].remove(key)
                    show_msg(input_win, [f"NPC removed: {key}"], wait_ms=1200)
                else:
                    show_msg(input_win, [f"No NPC with key: {key}"], wait_ms=1400)
                continue

            if len(tokens) >= 4 and tokens[1] == "create" and tokens[2] == "npc":
                if not player_state.get("admin"):
                    show_msg(input_win, ["Admin required."], wait_ms=1200)
                    continue
                key = tokens[3]
                if key in named_npcs:
                    show_msg(input_win, [f"NPC key already exists: {key}"], wait_ms=1400)
                    continue

                # Collect NPC data with editing capability
                npc_data = {
                    "name": "",
                    "role": "",
                    "dialogue": "",
                    "quest": None,
                    "conversation": None
                }

                while True:
                    # Display current data
                    input_win.clear()
                    input_win.box()
                    lines = [
                        f"Creating NPC: {key}",
                        f"1. Name: {npc_data['name'] or '(blank)'}",
                        f"2. Role: {npc_data['role'] or '(blank)'}",
                        f"3. Dialogue: {npc_data['dialogue'] or '(blank)'}",
                        f"4. Quest: {npc_data['quest']['title'] if npc_data['quest'] else '(none)'}",
                        f"5. Conversation: {'yes' if npc_data['conversation'] else 'no'}",
                        "",
                        "Choose: 1-5 to edit, 'create' to save, 'cancel' to abort"
                    ]
                    for i, ln in enumerate(lines, start=1):
                        try:
                            input_win.addstr(i, 2, ln)
                        except curses.error:
                            pass
                    input_win.refresh()
                    curses.echo()
                    try:
                        choice = input_win.getstr(len(lines), 2).decode("utf-8").strip().lower()
                    except Exception:
                        choice = ""
                    finally:
                        curses.noecho()

                    if choice == "cancel":
                        show_msg(input_win, ["NPC creation cancelled."], wait_ms=1200)
                        break
                    elif choice == "create":
                        if not npc_data["name"] or not npc_data["role"]:
                            show_msg(input_win, ["Name and role are required."], wait_ms=1200)
                            continue
                        created = create_npc_definition(key, npc_data)
                        if created:
                            show_msg(input_win, [f"NPC created: {key}"], wait_ms=1200)
                        else:
                            show_msg(input_win, ["Failed to create NPC."], wait_ms=1200)
                        break
                    elif choice == "1":
                        npc_data["name"] = prompt_input(input_win, "NPC name: ")
                    elif choice == "2":
                        npc_data["role"] = prompt_input(input_win, "NPC role: ")
                    elif choice == "3":
                        npc_data["dialogue"] = prompt_input(input_win, "NPC dialogue: ")
                    elif choice == "4":
                        quest_id = prompt_input(input_win, "Quest id (blank to remove): ")
                        if quest_id:
                            quest_title = prompt_input(input_win, "Quest title: ")
                            npc_data["quest"] = {"id": quest_id, "title": quest_title}
                        else:
                            npc_data["quest"] = None
                    elif choice == "5":
                        if prompt_input(input_win, "Add conversation JSON? (y/n): ").lower() == "y":
                            conv_json = prompt_input(input_win, "Enter conversation JSON: ")
                            try:
                                npc_data["conversation"] = __import__("json").loads(conv_json)
                            except Exception:
                                show_msg(input_win, ["Invalid JSON, conversation not set."], wait_ms=1200)
                        else:
                            npc_data["conversation"] = None
                    else:
                        show_msg(input_win, ["Invalid choice."], wait_ms=900)
                continue

            if len(tokens) >= 6 and tokens[1] == "place" and tokens[2] == "npc":
                if not player_state.get("admin"):
                    show_msg(input_win, ["Admin required."], wait_ms=1200)
                    continue
                key = tokens[3]
                x = tokens[4]
                y = tokens[5]
                if key not in named_npcs:
                    show_msg(input_win, [f"No NPC with key: {key}"], wait_ms=1400)
                    continue
                try:
                    loc = (int(x), int(y))
                except ValueError:
                    show_msg(input_win, ["Coordinates must be numbers."], wait_ms=1400)
                    continue
                tile = world_map.get(loc)
                if tile is None:
                    show_msg(input_win, ["No such location on the map."], wait_ms=1400)
                    continue
                tile.setdefault("npcs", [])
                if key not in tile["npcs"]:
                    tile["npcs"].append(key)
                show_msg(input_win, [f"Placed {key} at {loc}."], wait_ms=1200)
                continue

            if len(tokens) >= 6 and tokens[1] == "unplace" and tokens[2] == "npc":
                if not player_state.get("admin"):
                    show_msg(input_win, ["Admin required."], wait_ms=1200)
                    continue
                key = tokens[3]
                x = tokens[4]
                y = tokens[5]
                try:
                    loc = (int(x), int(y))
                except ValueError:
                    show_msg(input_win, ["Coordinates must be numbers."], wait_ms=1400)
                    continue
                tile = world_map.get(loc)
                if tile is None or key not in tile.get("npcs", []):
                    show_msg(input_win, ["NPC not placed there."], wait_ms=1400)
                    continue
                tile["npcs"].remove(key)
                show_msg(input_win, [f"Removed {key} from {loc}."], wait_ms=1200)
                continue

            if tokens == ["admin", "help"]:
                admin_help()
                continue

            show_msg(input_win, ["Unknown command."], wait_ms=1200)
            continue

        if command.startswith("talk"):
            tokens = command.split()
            if len(tokens) == 1:
                local_npcs = get_local_npc_keys()
                if not local_npcs:
                    show_msg(input_win, ["There is no one here to talk to."], wait_ms=1400)
                elif len(local_npcs) == 1:
                    talk_to_npc(local_npcs[0])
                else:
                    choice = choose_option("Who do you want to talk to?", local_npcs)
                    if choice is not None:
                        talk_to_npc(local_npcs[choice])
                continue
            if len(tokens) >= 2:
                talk_to_npc(tokens[1])
                continue

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
                # Refresh the map/info display before a possible encounter so the player sees the new room.
                render_map(map_win, player_state)
                render_info(info_win, player_state)
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
            input_win.addstr(1, 2, "Are you sure you want to quit? (y/n) ")
            input_win.refresh()
            curses.echo()
            confirm = input_win.getstr(2, 2).decode("utf-8").strip().lower()
            curses.noecho()
            if confirm == "y":
                input_win.clear()
                input_win.box()
                input_win.addstr(1, 2, "Thanks for playing!")
                input_win.refresh()
                curses.napms(1500)
                break
            else:
                show_msg(input_win, ["Quit cancelled."], wait_ms=900)

        elif command == "help":
            show_msg(input_win, ["Commands: north, south, east, west, talk, inventory, save, help, quit"], wait_ms=2200)

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