# This file is for rendering UI and info for the user.
import curses
import time

def render_info(win, player_state):
    win.clear()
    win.box()

    health = player_state.get("health", 100)
    food = player_state.get("food", 0)
    inventory = player_state.get("inventory", [])
    effects = player_state.get("status_effects", [])

    bar_width = 20
    health_filled = int((health / 100) * bar_width)
    food_filled = int((min(food, 100) / 100) * bar_width)

    # Flashing health bar if poisoned
    if "Poisoned" in effects:
        flash = player_state.get("_poison_flash", False)
        player_state["_poison_flash"] = not flash
        if flash:
            win.addstr(1, 2, "Health: [", curses.color_pair(1))
            for i in range(bar_width):
                char = "█" if i < health_filled else " "
                win.addstr(char, curses.color_pair(1))
            win.addstr("] " + f"{health}/100", curses.color_pair(1))
        else:
            win.addstr(1, 2, "Health: [" + " " * bar_width + "] " + f"{health}/100")
    else:
        player_state["_poison_flash"] = False
        win.addstr(1, 2, "Health: [", curses.color_pair(1))
        for i in range(bar_width):
            char = "█" if i < health_filled else " "
            win.addstr(char, curses.color_pair(1))
        win.addstr("] " + f"{health}/100", curses.color_pair(1))

    # Hunger bar
    win.addstr(2, 2, "Hunger: [", curses.color_pair(2))
    for i in range(bar_width):
        char = "▒" if i < food_filled else " "
        win.addstr(char, curses.color_pair(2))
    win.addstr("] " + f"{min(food, 100)}/100", curses.color_pair(2))

    # Status effects
    if effects:
        win.addstr(4, 2, f"Status: {', '.join(effects)}")

    win.addstr(5, 2, f"Inventory: {', '.join(inventory)}")
    win.addstr(6, 2, f"Quests: {player_state.get('active_quest', {}).get('title', 'None')}")
    win.refresh()
    
def get_command(win, player_state=None, info_win=None, render_info_func=None):
    win.clear()
    win.box()
    win.addstr(1, 2, "What do you want to do? ")
    win.refresh()
    typed = ""
    curses.noecho()
    win.keypad(True)
    timeout_ms = 150 if player_state and info_win and render_info_func else -1
    win.timeout(timeout_ms)
    last_update = time.time()

    while True:
        if player_state and info_win and render_info_func and (time.time() - last_update) >= 0.15:
            render_info_func(info_win, player_state)
            last_update = time.time()

        ch = win.getch()
        if ch == -1:
            continue
        if ch in (curses.KEY_ENTER, 10, 13):
            break
        if ch in (curses.KEY_BACKSPACE, 127, 8):
            if typed:
                typed = typed[:-1]
                win.move(2, 2)
                win.clrtoeol()
                win.addstr(2, 2, typed)
        elif ch == curses.KEY_RESIZE:
            pass
        else:
            try:
                char = chr(ch)
            except ValueError:
                char = ""
            if char and char.isprintable():
                typed += char
                win.addstr(2, 2, typed)
        win.refresh()

    win.timeout(-1)
    win.keypad(False)
    curses.noecho()
    return typed.strip()