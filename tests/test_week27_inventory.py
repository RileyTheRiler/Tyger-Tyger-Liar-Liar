
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'engine'))

from game import Game
from inventory_system import Item

def test_inventory_capacity():
    print("--- STARTING INVENTORY CAPACITY TEST ---")
    game = Game()
    inv = game.inventory_system

    # Base State
    print(f"Base Capacity: {inv.max_slots} slots, {inv.max_weight}kg")
    assert inv.max_slots == 10
    assert inv.max_weight == 20.0

    # Create a Heavy Item (50kg)
    heavy_rock = Item("rock", "Heavy Rock", "junk", "Very heavy.", weight=50.0, slots=1)

    # Try adding heavy item -> Should Fail
    print("Attempting to add 50kg rock...")
    added = inv.add_item(heavy_rock)
    assert not added
    print("-> Failed as expected.")

    # Create a Backpack (Storage Item)
    # +40kg capacity, +10 slots
    backpack = Item("backpack", "Hiking Backpack", "container", "Big bag.",
                    weight=1.0, slots=0,
                    storage_weight=40.0, storage_slots=10)

    # Add backpack
    inv.add_item(backpack)
    print("Added Backpack.")

    # Equip Backpack
    inv.equip_item("backpack")
    print(f"Equipped Backpack. New Capacity: {inv.max_slots} slots, {inv.max_weight}kg")

    assert inv.max_weight == 60.0 # 20 base + 40 bonus

    # Try adding heavy item again -> Should Succeed
    print("Attempting to add 50kg rock again...")
    added = inv.add_item(heavy_rock)
    assert added
    print("-> Succeeded.")

    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    test_inventory_capacity()
