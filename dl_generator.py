from defiant_parser_v0_2_4 import DefiantParser

def generate_dl(intent: str) -> str:
    intent = intent.lower()

    # very simple first pass (rule-based)
    if "defiant sky" in intent and "open" in intent:
        return """import tool glove_tools from library "defiant-ar-v1"

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
    return "# Could not map intent yet"


if __name__ == "__main__":
    parser = DefiantParser()

    user_intent = "When I open the Defiant Sky project, restore my layout and enable glove tools, and never delete without confirmation."

    dl_code = generate_dl(user_intent)

    print("=== Generated DL ===")
    print(dl_code)

    print("\n=== Parser Result ===")
    try:
        ast = parser.parse(dl_code)
        print("PASS")
        print(ast)
    except Exception as e:
        print("FAIL:", e)