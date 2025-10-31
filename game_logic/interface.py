# This file is for rendering UI and info for the user.
import curses

def render_info(win, player_state):
    win.clear()
    win.box()
    win.addstr(1, 2, f"Health: {player_state.get('health', 100)}")
    win.addstr(2, 2, f"Food: {player_state.get('food', 0)}")
    win.addstr(3, 2, f"Inventory: {', '.join(player_state['inventory'])}")

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
