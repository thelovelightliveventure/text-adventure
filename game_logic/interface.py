# This file is for rendering UI and info for the user.
import curses

def render_info(win, player_state):
    win.clear()
    win.box()

    health = player_state.get("health", 100)
    food = player_state.get("food", 0)
    inventory = player_state.get("inventory", [])

    # Health bar
    bar_width = 20
    health_filled = int((health / 100) * bar_width)
    health_bar = "[" + ("█" * health_filled) + (" " * (bar_width - health_filled)) + "]"

    # Hunger bar (based on food, capped at 100)
    food_capped = min(food, 100)
    food_filled = int((food_capped / 100) * bar_width)
    hunger_bar = "[" + ("▒" * food_filled) + (" " * (bar_width - food_filled)) + "]"

    win.addstr(1, 2, f"Health: {health_bar} {health}/100")
    win.addstr(2, 2, f"Hunger: {hunger_bar} {food_capped}/100")
    win.addstr(3, 2, f"Inventory: {', '.join(inventory)}")
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
