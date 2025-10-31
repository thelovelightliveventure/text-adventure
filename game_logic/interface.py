# This file is for rendering UI and info for the user.
import curses

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
        for _ in range(2):
            win.addstr(1, 2, "Health: [", curses.color_pair(1))
            for i in range(bar_width):
                char = "█" if i < health_filled else " "
                win.addstr(char, curses.color_pair(1))
            win.addstr("] " + f"{health}/100", curses.color_pair(1))
            win.refresh()
            curses.napms(150)
            win.addstr(1, 2, " " * (bar_width + 15))  # clear line
            win.refresh()
            curses.napms(150)
    else:
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
    win.refresh()
    
def get_command(win):
    win.clear()
    win.box()
    win.addstr(1, 2, "What do you want to do? ")
    win.refresh()
    curses.echo()
    command = win.getstr(2, 2).decode("utf-8").strip()
    curses.noecho()
    return command
