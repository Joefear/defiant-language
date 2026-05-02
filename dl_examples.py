from defiant_parser_v0_2_4 import DefiantParser

parser = DefiantParser()


def run_example(name, code):
    print(f"\n=== {name} ===")
    print(code)

    try:
        ast = parser.parse(code)
        print("\nPASS")
        print(ast)
    except Exception as e:
        print("\nFAIL:", e)


# =========================
# Example 1 — Workspace
# =========================
example1 = """import tool glove_tools from library "defiant-ar-v1"

define workspace DefiantSky

Hey workspace DefiantSky,

when project opens:
    restore layout last
    enable tool glove_tools on device left_wrist

You know what,
before action delete:
    require confirmation
    log action full
"""

# =========================
# Example 2 — Scene
# =========================
example2 = """import scene ForestClearing from library "defiant-game-v1"

define NPC old_hunter at location trail_start

Hey scene ForestClearing,

when player enters:
    spawn NPC old_hunter
"""

# =========================
# Run all
# =========================
if __name__ == "__main__":
    run_example("Workspace Example", example1)
    run_example("Scene Example", example2)