# ---------------------------------
# 1. GAME DATA & INITIAL SETUP
# ---------------------------------

# Each room has:
# - description: Text describing what the player sees upon entering.
# - items: A list of items that can be picked up.
# - exits: Directions or named paths (we'll treat them as next "locations" you can go to).
# - locked: Whether the room is locked initially.
# - enemy: If there is an enemy, store info about it (name, health, etc.).
# - triggers: Special story triggers or events that happen in the room.

rooms = {
    "library": {
        "description": (
            "You are in a grand library. The walls are lined with dusty books."
            " One particular book looks out of place on the shelf."
        ),
        "items": [],
        "exits": {"downstairs": "entrance_choice"},
        "locked": False,
        "enemy": None,
        "triggers": {
            "book_interaction": False,  # Once True, the hidden room is revealed
        },
    },
    "hidden_room": {
        "description": (
            "A secret room, dark and dusty. A faint light shines through a cracked window."
            " You see a statue holding a sword in its stone hands."
        ),
        "items": ["sword"],
        "exits": {"out": "library"},
        "locked": True,  # Unlocked when the player interacts with the book in the library
        "enemy": None,
        "triggers": {
            "statue_alive": True,  # If the statue has been defeated, set to False
        },
    },
    "entrance_choice": {
        "description": (
            "You're back at the spot where you woke up. The main door is locked tight."
            " You can still go UPSTAIRS to the library, or STRAIGHT down the hallway."
        ),
        "items": [],
        "exits": {
            # We'll handle the "go upstairs" or "go straight" logic separately
        },
        "locked": False,
        "enemy": None,
        "triggers": {}
    },
    # The hallway that leads to kitchen, ballroom, or another hallway
    "hallway": {
        "description": (
            "A long corridor with doors on each side. You can see signs pointing to the KITCHEN,"
            " the BALLROOM, or further down ANOTHER HALLWAY."
        ),
        "items": [],
        "exits": {
            "kitchen": "kitchen",
            "ballroom": "ballroom",
            "hallway2": "hallway2",
            "back": "entrance_choice"
                },
        "locked": False,
        "enemy": None,
        "triggers": {}
    },
    "kitchen": {
        "description": (
            "A dusty kitchen with old pots and pans scattered around. There might be something to eat here."
        ),
        "items": ["food"],  # 'food' will heal the player
        "exits": {"back": "hallway"},
        "locked": False,
        "enemy": None,
        "triggers": {}
    },
    "ballroom": {
        "description": (
            "An ornate ballroom with a grand chandelier. You find a clue scribbled on the wall."
            " It reads: 'To reach the key in the dark below, answer the riddle or suffer woe.'"
        ),
        "items": [],  # No direct items, but it gives a clue about the basement
        "exits": {"back": "hallway"},
        "locked": False,
        "enemy": None,
        "triggers": {}
    },
    "hallway2": {
        "description": (
            "Another hallway with two doors. The signs say BEDROOM and OFFICE. The other doors are locked."
        ),
        "items": [],
        "exits": {
            "bedroom": "bedroom", 
            "office": "office", 
            "back": "hallway", 
            "basement": "basement"
                 },
        "locked": False,
        "enemy": None,
        "triggers": {}
    },
    "bedroom": {
        "description": (
            "You enter a lavish bedroom. Inside, you see a figure turned away from you. "
            "It looks like a princess, but something isn't right..."
        ),
        "items": [],
        "exits": {"back": "hallway2"},
        "locked": False,
        "enemy": {
            "name": "zombie princess",
            "health": 1,
            "damage": 3  # If you fight without a sword, or you can define logic differently
        },
        "triggers": {}
    },
    "office": {
        "description": (
            "A small office cluttered with old papers. There's a DAGGER on the desk and a POTION on a shelf."
        ),
        "items": ["dagger", "potion"],
        "exits": {"back": "hallway2"},
        "locked": False,
        "enemy": None,
        "triggers": {}
    },
    "basement": {
        "description": (
            "A dark, musty basement filled with cobwebs. You sense danger ahead. "
            "Shadows shift, revealing enemies guarding a final key."
        ),
        "items": ["final key"],  # The key to escape
        "exits": {"up": "hallway2"},
        "locked": True,  # Initially locked, you need the key from the zombie princess to get in
        "enemy": {
            "name": "basement creatures",
            "health": 2,
            "damage": 4
        },
        "triggers": {}
    },
}

# Player state
player_state = {
    "current_room": "entrance_choice",  # Start where they make the initial decision
    "inventory": [],
    "health": 20,
    "has_basement_key": False,  # From the zombie princess
}

game_running = True

# ---------------------------------
# 2. INTRO & INITIAL PROMPT
# ---------------------------------

def show_intro():
    print("Hello! Welcome to Castle Escape!")
    print("Here is how to play the game:")
    print(" - Type 'take <item>' on ONE line to pick up items, e.g., 'take food'.")
    print(" - Type 'look <item>' on ONE line to examine items, e.g., 'look book'.")
    print(" - Type 'use <item>' on ONE line to use an item in your inventory, e.g., 'use potion'.")
    print(" - Type 'go' or 'move' to see where you can go next.")
    print(" - Type 'quit' or 'exit' to stop the game.")
    print("Are you ready to begin? Type 'ready'.")

# ---------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------

def describe_current_room():
    """Show the room description and items if the room is unlocked."""
    current_room = rooms[player_state["current_room"]]
    print(current_room["description"])
    
    # List available items
    if current_room["items"]:
        print("Items you see here:", ", ".join(current_room["items"]))

def move_player():
    """
    Prompt the player for possible directions or next rooms.
    For story convenience, we'll define how the game flows
    instead of strictly using a dictionary-based exit check.
    """
    current_room_id = player_state["current_room"]
    current_room_data = rooms[current_room_id]

    # Special logic for the 'entrance_choice' to handle "upstairs" vs "straight"
    if current_room_id == "entrance_choice":
        print("You can go 'upstairs' to the library or 'straight' down the hallway.")
        choice = input("> ").strip().lower()
        if choice in ["upstairs", "library"]:
            player_state["current_room"] = "library"
            describe_current_room()
            return
        elif choice in ["straight", "hallway"]:
            player_state["current_room"] = "hallway"
            describe_current_room()
            return
        else:
            print("You can't go that way.")
            return

    # Otherwise, show exits for the current room
    exits = current_room_data["exits"]
    if not exits:
        print("There seems to be nowhere else to go from here.")
        return
    
    print(f"Possible paths: {', '.join(exits.keys())}")
    choice = input("> ").strip().lower()
    if choice in exits:
        # Check if the chosen room is locked
        next_room_id = exits[choice]
        if rooms[next_room_id]["locked"]:
            # If it's the basement, check if the player has the key
            if next_room_id == "basement" and player_state["has_basement_key"]:
                rooms[next_room_id]["locked"] = False
                print("You unlock the basement door with the key you found!")
            else:
                print("It's locked. You can't go there yet.")
                return
        
        # Move to the next room
        player_state["current_room"] = next_room_id
        describe_current_room()
        check_for_special_triggers()
        check_for_combat()
    else:
        print("You can't go that way.")

def check_for_special_triggers():
    """
    Handle special room-based logic or story events.
    - Library: If the player interacts with a special book, unlock hidden_room.
    - hidden_room: If the player picks up the sword, the statue attacks.
    - Etc.
    (We'll keep it simple and allow the 'interaction' via commands.)
    """
    # Not invoked automatically here, but you might expand it if you want certain events
    # to trigger the moment the player enters the room.
    pass

def check_for_combat():
    """If there's an enemy in the current room, handle it."""
    current_room_id = player_state["current_room"]
    enemy_data = rooms[current_room_id]["enemy"]
    
    if enemy_data:
        enemy_name = enemy_data["name"]
        print(f"A {enemy_name} appears!")
        
        # We'll handle specifics in a fight or flee scenario:
        fight_or_flee = input("Do you fight or flee? (fight/flee) > ").strip().lower()
        if current_room_id == "hidden_room" and rooms["hidden_room"]["triggers"]["statue_alive"]:
            # Statue logic
            if fight_or_flee == "fight":
                # Player loses 5 health if they fight but gets the sword
                # Actually, they already 'picked' the sword. We'll check if they have it.
                print("You fight the statue! You lose 5 health, but you defeat it.")
                player_state["health"] -= 5
                print(f"Your health is now {player_state['health']}.")
                # Statue is defeated, so set statue_alive to False
                rooms["hidden_room"]["triggers"]["statue_alive"] = False
                rooms["hidden_room"]["enemy"] = None
            else:
                # flee => lose 10, don't get the sword
                print("You flee! The statue strikes you as you escape.")
                player_state["health"] -= 10
                print(f"You lose 10 health. Your health is now {player_state['health']}.")
                # Remove the sword if you managed to pick it up
                if "sword" in player_state["inventory"]:
                    print("In your panic, you drop the sword!")
                    player_state["inventory"].remove("sword")
                # The statue remains
            check_defeat_condition()

        elif current_room_id == "bedroom":
            # Zombie princess logic
            has_sword = "sword" in player_state["inventory"]
            if fight_or_flee == "fight":
                if has_sword:
                    print("You strike the zombie princess with your sword, defeating her!")
                    rooms["bedroom"]["enemy"] = None
                  
                    if(player_state["health"] > 0):
                          # She drops a key
                        print("You find a small key on her. It might open the basement.")
                        player_state["has_basement_key"] = True
                else:
                    # Use dagger or nothing
                    if "dagger" in player_state["inventory"]:
                        print("You fight the zombie princess with your dagger, but you take damage.")
                        player_state["health"] -= 5
                        print(f"Your health is now {player_state['health']}.")
                        rooms["bedroom"]["enemy"] = None
                    
                        if(player_state["health"] > 0):
                             print("You find a small key on her. It might open the basement.")
                             player_state["has_basement_key"] = True
                    else:
                        print("You have no weapon! The princess bites you!")
                        player_state["health"] -= 10
                        print(f"Your health is now {player_state['health']}.")
                        if player_state["health"] > 0:
                            print("You manage to push her away and run!")
                        else:
                            check_defeat_condition()
            else:
                # flee => lose some health?
                print("You flee the bedroom, taking a hit from the zombie princess!")
                player_state["health"] -= 7
                print(f"Your health is now {player_state['health']}.")
                check_defeat_condition()
            # End bedroom combat
          
        elif current_room_id == "basement":
            if fight_or_flee == "fight":
                # 1) The user is fighting
                if "sword" in player_state["inventory"]:
                    # Fighting with a sword
                    print("You fight fiercely with your sword, striking down the basement creatures!")
                     # Let's say we don't take damage if we have a sword, or define small damage if you prefer
                    damage_taken = 0  # or maybe 2 or 3
                    player_state["health"] -= damage_taken
                    print(f"You take {damage_taken} damage. Your health is now {player_state['health']}.")
            
            # Mark the enemy as defeated
                    rooms["basement"]["enemy"] = None
            
            # Auto-pick up the final key if you want
                    if "final key" in rooms["basement"]["items"] and (player_state["health"] > 0):
                      rooms["basement"]["items"].remove("final key")
                      player_state["inventory"].append("final key")
                      print("You find a final key on the ground and take it!")

                elif "dagger" in player_state["inventory"]:
                # Fighting with a dagger
                    print("You fight with your dagger...")
                    damage_taken = 5
                    player_state["health"] -= damage_taken
            
                    if player_state["health"] > 0:
                      print(f"You take {damage_taken} damage, but manage to prevail.")
                      print(f"Your health is now {player_state['health']}.")
                      rooms["basement"]["enemy"] = None

                # Auto-pick up final key if desired
                    if "final key" in rooms["basement"]["items"] and (player_state["health"] > 0):
                     rooms["basement"]["items"].remove("final key")
                     player_state["inventory"].append("final key")
                     print("You find a final key on the ground and take it!")
                    else:
                      print(f"You take {damage_taken} damage... it's too much!")
                      print(f"Your health is now {player_state['health']}.")
                      rooms["basement"]["enemy"] = None

                      check_defeat_condition()

                else:
                     # Fighting with no weapon
                    print("Fighting barehanded is tough. The creatures lash out!")
                    damage_taken = 10
                    player_state["health"] -= damage_taken
            
                    if player_state["health"] > 0:
                      print(f"You take {damage_taken} damage, but somehow prevail.")
                      print(f"Your health is now {player_state['health']}.")
                      rooms["basement"]["enemy"] = None

                # Possibly pick up the key if you want them to still get it
                    if "final key" in rooms["basement"]["items"]:
                       rooms["basement"]["items"].remove("final key")
                       player_state["inventory"].append("final key")
                       print("You find a final key on the ground and take it!")
                    else:
                      print(f"You take {damage_taken} damage... it's too much!")
                      print(f"Your health is now {player_state['health']}.")
                      rooms["basement"]["enemy"] = None

                      check_defeat_condition()

            else:
                # 2) The user flees
                print("You try to flee from the basement creatures!")
                damage_taken = 5  # maybe the creatures get a free hit as you flee
                player_state["health"] -= damage_taken

                if player_state["health"] > 0:
                    print(f"You lose {damage_taken} health but escape for now.")
                    print(f"Your health is now {player_state['health']}.")
                else:
                     print(f"You lose {damage_taken} health... it's too much!")
                     print(f"Your health is now {player_state['health']}.")

                     check_defeat_condition()


def look_command(args):
    """Handles 'look' or 'inspect' commands."""
    current_room_id = player_state["current_room"]
    if len(args) == 1:
        describe_current_room()
    else:
        item_to_look = args[1]
        # Special case: if they type 'look book' in the library to unlock hidden room
        if current_room_id == "library" and item_to_look == "book":
            # Unlock the hidden room
            if not rooms["library"]["triggers"]["book_interaction"]:
                rooms["library"]["triggers"]["book_interaction"] = True
                rooms["hidden_room"]["locked"] = False
                rooms["library"]["exits"]["secret"] = "hidden_room"
                print("You pull the strange book. A secret door opens to a hidden room!")
            else:
                print("You've already discovered the hidden room.")
        else:
            # Check if the item is in the room or in the inventory
            if item_to_look in rooms[current_room_id]["items"] or item_to_look in player_state["inventory"]:
                print(f"You examine the {item_to_look}. It's quite interesting!")
            else:
                print(f"You don't see a {item_to_look} here.")

def take_item(item_name):
    current_room_id = player_state["current_room"]
    current_room_data = rooms[current_room_id]
    if item_name in current_room_data["items"]:
        current_room_data["items"].remove(item_name)
        player_state["inventory"].append(item_name)
        print(f"You picked up the {item_name}.")

        # If they pick up the sword in the hidden_room, the statue comes to life now
        if current_room_id == "hidden_room" and item_name == "sword":
            print("As you grab the sword, the statue comes to life behind you!")
            
            # Assign statue data ONLY at this point
            rooms["hidden_room"]["enemy"] = {
                "name": "statue",
                "health": 1,
                "damage": 0
            }
            check_for_combat()

        # If they pick up 'food' in the kitchen, they eat it automatically
        if item_name == "food":
            print("You eat the food and feel better.")
            player_state["health"] += 5
            print(f"Your health is now {player_state['health']}.")
    else:
        print(f"You can't find {item_name} here.")

def use_item(item_name, target=None):
    """
    Rule-based 'use' command. Adjust logic to fit your items and puzzles.
    E.g., use 'potion' to heal, use 'rusty key' on something, etc.
    """
    if item_name not in player_state["inventory"]:
        print("You don't have that item.")
        return

    # Example uses
    if item_name == "potion":
        print("You drink the potion and feel refreshed.")
        player_state["health"] += 10
        player_state["inventory"].remove("potion")
        print(f"Your health is now {player_state['health']}.")
    else:
        print(f"You can't use {item_name} right now.")

def check_defeat_condition():
    """If the player's health is 0 or below, they lose."""
    if player_state["health"] <= 0:
        print("You have died!")
        end_game()

def check_victory_condition():
    """
    Check if the player used the 'final key' at the entrance door, for instance.
    We'll simulate that once they have 'final key' in inventory and they're back at 'entrance_choice',
    they can unlock the front door and escape.
    """
    if "final key" in player_state["inventory"] and player_state["current_room"] == "entrance_choice":
        print("You use the final key on the main door. It unlocks with a loud click!")
        print("You push the door open and escape the castle. Congratulations, you win!")
        end_game()

def end_game():
    """Stop the game loop."""
    global game_running
    game_running = False

# ---------------------------------
# 4. MAIN GAME LOOP
# ---------------------------------

def main_game_loop():
    show_intro()
    while True:
        user_input = input("> ").strip().lower()
        if user_input == "ready":
            print("You wake up in an old castle. The main door is locked.")
            print("You can go 'UPSTAIRS' to the library, or 'STRAIGHT' down the hallway.")
            break
        elif user_input in ["quit", "exit"]:
            print("Goodbye!")
            return
        else:
            print("Type 'ready' when you're ready to begin, or 'quit'/'exit' to stop.")

    describe_current_room()  # Show the initial situation

    while game_running:
        command_input = input("> ").strip().lower()
        if not command_input:
            continue
        
        parts = command_input.split()
        verb = parts[0]

        if verb in ["quit", "exit"]:
            print("Goodbye!")
            end_game()

        elif verb in ["look", "inspect"]:
            look_command(parts)

        elif verb in ["take", "pick"]:
            if len(parts) < 2:
                print("Take what?")
            else:
                item_name = parts[-1]
                take_item(item_name)

        elif verb == "use":
            if len(parts) < 2:
                print("Use what?")
            else:
                item_name = parts[1]
                if "on" in parts:
                    on_index = parts.index("on")
                    if on_index + 1 < len(parts):
                        target_name = parts[on_index+1]
                        use_item(item_name, target_name)
                    else:
                        print("Use item on what?")
                else:
                    use_item(item_name)

        elif verb in ["go", "move"]:
            move_player()

        else:
            print("Invalid command. Try 'look', 'take', 'use', or 'go'.")

        # Check victory condition after each command
        check_victory_condition()
        # Check defeat condition as well
        check_defeat_condition()

# ---------------------------------
# 5. RUN THE GAME
# ---------------------------------

if __name__ == "__main__":
    main_game_loop()
