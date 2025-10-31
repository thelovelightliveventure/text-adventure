# This file is for rendering UI and info for the user.
import curses

def render_info(win, player_state):
    win.clear()
    win.box()

    health = player_state.get("health", 100)
    food = player_state.get("food", 0)
    inventory = player_state.get("inventory", [])

    bar_width = 20

    # Animate health bar
    win.addstr(1, 2, "Health: [", curses.color_pair(1))
    for i in range(bar_width):
        if i < int((health / 100) * bar_width):
            win.addstr("█", curses.color_pair(1))
        else:
            win.addstr(" ", curses.color_pair(1))
        win.refresh()
        curses.napms(15)
    win.addstr("] " + f"{health}/100", curses.color_pair(1))

    # Animate hunger bar
    win.addstr(2, 2, "Hunger: [", curses.color_pair(2))
    for i in range(bar_width):
        if i < int((min(food, 100) / 100) * bar_width):
            win.addstr("▒", curses.color_pair(2))
        else:
            win.addstr(" ", curses.color_pair(2))
        win.refresh()
        curses.napms(15)
    win.addstr("] " + f"{min(food, 100)}/100", curses.color_pair(2))

    # Inventory
    win.addstr(4, 2, f"Inventory: {', '.join(inventory)}")
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
