# Consumable templates — edit / extend this list to add foods, potions, fruits, etc.
# Each entry:
#  - name: descriptive name (for your reference)
#  - match: list of substrings to match against inventory item lowercased
#  - food: integer change to player_state["food"] (can be negative)
#  - hp: integer change to health (optional)
#  - effect: optional status effect to add (string) or remove (use negative semantics in your own logic)
food = [
    {
        "name": "Deer Meat",
        "match": ["deer", "meat"], 
        "food": 25, "hp": 10,  
        "effect": "Well Fed"
    },
    {
        "name": "Boar Meat",
        "match": ["boar", "vvoard", "meat"],
        "food": 40, "hp": 10,
        "effect": "Well Fed"
    },
    {
        "name": "Generic Meat",
        "match": ["meat"],
        "food": 30, "hp": 10,
        "effect": "Well Fed"
    },
    {
        "name": "Apple",
        "match": ["apple", "fruit"], 
        "food": 10, "hp": 5
    },
    {
        "name": "Wild Mushroom",
        "match": ["mushroom"],
        "food": 5,  "hp": -5,
        "effect": "Poisoned"
    }
]
