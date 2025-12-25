
class ObjectEditor:
    """
    Helper for generating object interaction JSON.
    """
    @staticmethod
    def create_object_template(name, description):
        return {
            name.lower().replace(" ", "_"): {
                "name": name,
                "description": description,
                "type": "interactable",
                "interactions": {
                    "use": {
                        "text": f"You use the {name}."
                    },
                    "examine": {
                        "text": description
                    }
                }
            }
        }

class InventoryBalancer:
    """
    Helper to check item weights and balance.
    """
    @staticmethod
    def check_balance(items_list):
        total_weight = sum(i.get("weight", 0) for i in items_list)
        print(f"Total Weight: {total_weight}")
        # Logic to suggest changes?
        pass
