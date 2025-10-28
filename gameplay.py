from game_logic import (
    GossipGenerator, 
    named_npcs, 
    load_from_code, 
    generate_save_code, 
    render_map, 
    describe_location, 
    get_command
)

# Default starting state
default_state = {
    "name": "User1",
    "role": "Explorer",
    "location": [0, 0],
    "inventory": ["backpack", "map"],
    "quests_completed": [],
    "explored": [(0, 0)],
    "npc_flags": {}     # e.g., {"Blacksmith": {"met": True, "quest_accepted": True}}
}

# Load or start new game
choice = input("Do you want to enter a save code to continue? (y/n): ").lower()
if choice == "y":
    code = input("Paste your save code: ")
    player_state = load_from_code(code) or default_state
else:
    player_state = default_state

# Create gossip generator
gossip_gen = GossipGenerator()

# Game loop
while True:
    print(f"\nYou are at {player_state['location']}")
    render_map(player_state["location"], player_state["explored"])
    describe_location(player_state["location"], gossip_gen, player_state)

    command = get_command()

    if command in ["north", "south", "east", "west"]:
        x, y = player_state["location"]
        if command == "north": y += 1
        elif command == "south": y -= 1
        elif command == "east": x += 1
        elif command == "west": x -= 1
        player_state["location"] = [x, y]
        if (x, y) not in player_state["explored"]:
            player_state["explored"].append((x, y))
        print(f"You move {command}.")
    
    elif command == "inventory":
        print("Inventory:", player_state["inventory"])
    
    elif command == "save":
        code = generate_save_code(player_state)
        print("\nYour save code:")
        print(code)
    
    elif command == "quit":
        print("Thanks for playing!")
        break
    
    elif command == "help":
        print("Commands: north, south, east, west, inventory, save, help, quit")
    
    else:
        print("Unknown command. Try north, south, east, west, inventory, save, help, or quit.")