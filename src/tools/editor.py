import json
import os
from engine.case_file_system import CaseFileSystem, CaseFile, Evidence
from engine.theories import THEORY_DATA

class EditorTools:
    def __init__(self):
        self.case_system = CaseFileSystem()
        # Initialize theory data path assumption
        self.theory_data_path = "data/theories.json"

    def run(self):
        while True:
            print("\n=== TYGER TYGER EDITOR TOOLKIT ===")
            print("1. Case File Builder")
            print("2. Evidence Builder")
            print("3. Theory/Board Editor (Not implemented - edit JSON directly)")
            print("4. Exit")

            choice = input("Select tool: ")

            if choice == "1":
                self.case_builder()
            elif choice == "2":
                self.evidence_builder()
            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    def case_builder(self):
        print("\n--- Case File Builder ---")
        case_id = input("Case ID: ").strip()
        if not case_id: return

        case = self.case_system.get_case(case_id)
        if case:
            print(f"Editing existing case: {case.title}")
        else:
            title = input("Case Title: ").strip()
            desc = input("Description: ").strip()
            case = self.case_system.create_case(case_id, title, desc)
            print("Case created.")

        while True:
            print(f"\nCase: {case.title}")
            print("1. Add Suspect")
            print("2. Add Witness")
            print("3. Add Timeline Event")
            print("4. Save & Exit")

            sub = input("> ")
            if sub == "1":
                sus = input("Suspect ID: ")
                self.case_system.add_suspect(case.id, sus)
            elif sub == "2":
                wit = input("Witness ID: ")
                self.case_system.add_witness(case.id, wit)
            elif sub == "3":
                time = input("Time: ")
                desc = input("Event: ")
                self.case_system.add_timeline_event(case.id, time, desc)
            elif sub == "4":
                self.case_system.save_data()
                break

    def evidence_builder(self):
        print("\n--- Evidence Builder ---")
        ev_id = input("Evidence ID: ").strip()
        if not ev_id: return

        ev = self.case_system.get_evidence(ev_id)
        if ev:
            print(f"Editing existing evidence: {ev.name}")
            # Simplified editing - just print for now
        else:
            name = input("Name: ")
            desc = input("Description: ")
            typ = input("Type (physical, testimonial, psychic): ")
            cred = input("Credibility (clean, contaminated, disputed): ")
            case_id = input("Linked Case ID: ")

            ev = Evidence(ev_id, name, desc, typ, cred, case_id)
            self.case_system.add_evidence(ev)
            self.case_system.save_data()
            print("Evidence saved.")

if __name__ == "__main__":
    tool = EditorTools()
    tool.run()
