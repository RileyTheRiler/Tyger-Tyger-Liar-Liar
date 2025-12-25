import os
import shutil
import sys

def main():
    print("Beginning Tyger Tyger Deployment Setup...")

    # Target structure
    # /deploy/
    #   /saves/
    #   /scripts/
    #   /scenes/
    #   /board_theories/
    #   /evidence/
    #   /parser_hooks/
    #   /debug_logs/

    BASE_DIR = os.getcwd()
    DEPLOY_DIR = os.path.join(BASE_DIR, "deploy")

    # Create main directory
    if not os.path.exists(DEPLOY_DIR):
        os.makedirs(DEPLOY_DIR)
        print(f"Created {DEPLOY_DIR}")

    dirs_to_create = [
        "saves",
        "scripts",
        "scenes",
        "board_theories",
        "evidence",
        "parser_hooks",
        "debug_logs",
        "src",
        "web"
    ]

    for d in dirs_to_create:
        path = os.path.join(DEPLOY_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created {path}")

    # Copy Data
    print("Copying data...")

    # Scenes
    src_scenes = os.path.join(BASE_DIR, "data", "scenes")
    if os.path.exists(src_scenes):
        for item in os.listdir(src_scenes):
            s = os.path.join(src_scenes, item)
            d = os.path.join(DEPLOY_DIR, "scenes", item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    # Theories
    src_theories = os.path.join(BASE_DIR, "data", "theories")
    if os.path.exists(src_theories):
         for item in os.listdir(src_theories):
            s = os.path.join(src_theories, item)
            d = os.path.join(DEPLOY_DIR, "board_theories", item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    # Evidence
    src_evidence = os.path.join(BASE_DIR, "data", "evidence.json")
    if os.path.exists(src_evidence):
        shutil.copy2(src_evidence, os.path.join(DEPLOY_DIR, "evidence", "evidence.json"))

    # Copy Source Code (Runtime requirement)
    print("Copying source code...")
    shutil.copytree(os.path.join(BASE_DIR, "src"), os.path.join(DEPLOY_DIR, "src"), dirs_exist_ok=True)

    # Copy Web
    print("Copying web files...")
    shutil.copytree(os.path.join(BASE_DIR, "web"), os.path.join(DEPLOY_DIR, "web"), dirs_exist_ok=True)

    # Copy Game Scripts
    print("Copying entry points...")
    shutil.copy2(os.path.join(BASE_DIR, "game.py"), os.path.join(DEPLOY_DIR, "game.py"))
    if os.path.exists(os.path.join(BASE_DIR, "game.config.json")):
        shutil.copy2(os.path.join(BASE_DIR, "game.config.json"), os.path.join(DEPLOY_DIR, "game.config.json"))

    # Copy Launcher Scripts
    launchers = ["run_cli.sh", "run_cli.bat", "run_web.sh", "run_web.bat"]
    for l in launchers:
        src_l = os.path.join(BASE_DIR, l)
        if os.path.exists(src_l):
             shutil.copy2(src_l, os.path.join(DEPLOY_DIR, l))
             print(f"Copied {l}")

    # Create README
    with open(os.path.join(DEPLOY_DIR, "README.txt"), "w") as f:
        f.write("Tyger Tyger - Internal Build\n")
        f.write("==============================\n")
        f.write("To run the game:\n")
        f.write("  Run 'run_cli.sh' (Linux/Mac) or 'run_cli.bat' (Windows)\n")
        f.write("\n")
        f.write("Directory Structure:\n")
        f.write("  /saves/          - Save files stored here\n")
        f.write("  /scenes/         - Scene data\n")
        f.write("  /board_theories/ - Theory definitions\n")
        f.write("  /debug_logs/     - Logs\n")

    print("\nDeployment setup complete in ./deploy/")

if __name__ == "__main__":
    main()
