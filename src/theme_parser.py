import os
import re

# Expanded Global Properties
# "virtual": True means "Don't write this as key="val" at the top of the file"
THEME_GLOBALS = {
    # --- GROUP: General ---
    "title-text": {"label": "Title Text", "type": "text", "group": "General",
                   "desc": "Text displayed at the top of the screen."},
    "title-font": {"label": "Title Font", "type": "font", "group": "General", "desc": "Font used for the title."},
    "title-color": {"label": "Title Color", "type": "color", "group": "General", "desc": "Color of the title text."},

    # --- GROUP: Appearance ---
    "desktop-image": {"label": "Desktop Image", "type": "file", "group": "Appearance",
                      "desc": "Background image for the menu."},
    "desktop-color": {"label": "Desktop Color", "type": "color", "group": "Appearance",
                      "desc": "Background color if no image is used."},

    # --- GROUP: Menu Layout ---
    "menu-position": {
        "label": "Menu Position",
        "type": "dropdown",
        "group": "Menu Layout",
        "options": ["Northwest", "North", "Northeast", "West", "Center", "East", "Southwest", "South", "Southeast"],
        "desc": "Position of the boot menu on the screen.",
        "virtual": True
    },
    "terminal-font": {"label": "Terminal Font", "type": "font", "group": "Menu Layout",
                      "desc": "Font used in the terminal box."},

    # --- GROUP: Progress Bar ---
    "progress-style": {
        "label": "Progress Style",
        "type": "dropdown",
        "group": "Progress Bar",
        "options": ["bar"],  # Removed "circle" temporarily for safety
        "desc": "Style of the timeout indicator.",
        "virtual": True
    },
    "progress-color": {
        "label": "Progress Color", "type": "color", "group": "Progress Bar", "desc": "Color of the filled portion.",
        "virtual": True
    },
    "progress-bg-color": {
        "label": "Progress Background", "type": "color", "group": "Progress Bar",
        "desc": "Color of the empty portion (track).",
        "virtual": True
    },

    # --- GROUP: Styled Box ---
    "message-font": {"label": "Message Font", "type": "font", "group": "Styled Box",
                     "desc": "Font used for footer messages."},
    "message-color": {"label": "Message Color", "type": "color", "group": "Styled Box",
                      "desc": "Color of the message text."},
    "box-border-color": {"label": "Box Border Color", "type": "color", "group": "Styled Box",
                         "desc": "Color of the menu border.", "virtual": True},
    "box-bg-color": {"label": "Box Background", "type": "color", "group": "Styled Box",
                     "desc": "Background color of the menu box.", "virtual": True},
    "selected-item-color": {"label": "Selected Item Text", "type": "color", "group": "Styled Box",
                            "desc": "Text color of the highlighted entry.", "virtual": True},
    "selected-item-bg-color": {"label": "Selected Item BG", "type": "color", "group": "Styled Box",
                               "desc": "Background color of the highlighted entry.", "virtual": True}
}

POSITION_MAP = {
    "Northwest": ("5%", "5%"), "North": ("25%", "5%"), "Northeast": ("45%", "5%"),
    "West": ("5%", "30%"), "Center": ("25%", "30%"), "East": ("45%", "30%"),
    "Southwest": ("5%", "55%"), "South": ("25%", "55%"), "Southeast": ("45%", "55%"),
}


def parse_theme(theme_path):
    """Parses a GRUB theme.txt file."""
    properties = {}
    if not os.path.exists(theme_path): return {}

    try:
        with open(theme_path, 'r') as f:
            content = f.read()

        # 1. Parse Simple Globals
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'): continue
            match = re.match(r'^([\w\-]+)\s*:\s*"?([^"]*)"?', line)
            if match:
                key = match.group(1)
                val = match.group(2)
                if key in THEME_GLOBALS:
                    properties[key] = val

        # 2. Parse Progress Bar Block
        # We look for the fg_color inside a progress_bar block to populate our 'progress-color' virtual key
        pb_match = re.search(r'\+\s*progress_bar\s*\{([^}]*)\}', content, re.DOTALL)
        if pb_match:
            block = pb_match.group(1)
            if m := re.search(r'fg_color\s*=\s*"?([^"\n]*)"?', block):
                properties["progress-color"] = m.group(1)
            if m := re.search(r'bg_color\s*=\s*"?([^"\n]*)"?', block):
                properties["progress-bg-color"] = m.group(1)
            properties["progress-style"] = "bar"

        # 3. Parse Menu Position
        bm_match = re.search(r'\+\s*boot_menu\s*\{([^}]*)\}', content, re.DOTALL)
        if bm_match:
            block = bm_match.group(1)
            left_m = re.search(r'left\s*=\s*"?([\d%]+)"?', block)
            top_m = re.search(r'top\s*=\s*"?([\d%]+)"?', block)
            if left_m and top_m:
                l_val, t_val = left_m.group(1), top_m.group(1)
                for name, coords in POSITION_MAP.items():
                    if coords[0] == l_val and coords[1] == t_val:
                        properties["menu-position"] = name
                        break

    except Exception as e:
        print(f"Error parsing theme: {e}")

    return properties


def save_theme(theme_path, data_dict):
    """Updates keys in the theme file, handling virtual blocks correctly."""
    if not os.path.exists(theme_path): return None

    try:
        with open(theme_path, 'r') as f:
            content = f.read()

        lines = content.splitlines()
        new_lines = []
        processed_keys = set()

        # 1. Update Globals (Skip Virtuals)
        for line in lines:
            stripped = line.strip()
            match = re.match(r'^([\w\-]+)\s*:\s*"?([^"]*)"?', stripped)

            # If it's a global key assignment (and not inside a block)
            if match and not stripped.startswith('#') and '{' not in stripped:
                key = match.group(1)
                # Only write if it's NOT virtual
                if key in data_dict and key in THEME_GLOBALS and not THEME_GLOBALS[key].get("virtual"):
                    new_lines.append(f'{key}: "{data_dict[key]}"')
                    processed_keys.add(key)
                # If it's a key we manage but it IS virtual, we SKIP writing it here (to remove old garbage)
                elif key in THEME_GLOBALS and THEME_GLOBALS[key].get("virtual"):
                    pass
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Append missing non-virtual globals
        for key, val in data_dict.items():
            if key in THEME_GLOBALS and not THEME_GLOBALS[key].get("virtual"):
                if key not in processed_keys:
                    new_lines.append(f'{key}: "{val}"')

        final_content = "\n".join(new_lines) + "\n"

        # 2. Construct Progress Bar Block
        # We REBUILD the block entirely to ensure it's valid
        p_color = data_dict.get("progress-color", "#fff")
        p_bg = data_dict.get("progress-bg-color", "#000")

        # Valid GRUB syntax for a progress bar
        # id="__timeout__" is REQUIRED for it to work as a timeout counter
        new_pb_block = f"""
+ progress_bar {{
    id = "__timeout__"
    left = 15%
    top = 90%
    width = 70%
    height = 20
    fg_color = "{p_color}"
    bg_color = "{p_bg}"
    border_color = "{p_color}"
    text = "@TIMEOUT_NOTIFICATION_LONG@"
    font = "Sans Regular 12"
    text_color = "#ffffff"
}}
"""
        # Remove existing progress_bar block if present
        final_content = re.sub(r'\+\s*progress_bar\s*\{[^}]*\}', '', final_content, flags=re.DOTALL)
        # Append new block
        final_content += new_pb_block

        # 3. Update Boot Menu (Position)
        if "menu-position" in data_dict:
            pos_name = data_dict["menu-position"]
            if pos_name in POSITION_MAP:
                left_val, top_val = POSITION_MAP[pos_name]

                if re.search(r'\+\s*boot_menu\s*\{', final_content):
                    def replace_block(m):
                        block_content = m.group(1)
                        if re.search(r'left\s*=', block_content):
                            block_content = re.sub(r'left\s*=\s*"?[^"\n]*"?', f'left = {left_val}', block_content)
                        else:
                            block_content += f'\n  left = {left_val}'

                        if re.search(r'top\s*=', block_content):
                            block_content = re.sub(r'top\s*=\s*"?[^"\n]*"?', f'top = {top_val}', block_content)
                        else:
                            block_content += f'\n  top = {top_val}'
                        return f'+ boot_menu {{{block_content}}}'

                    final_content = re.sub(r'\+\s*boot_menu\s*\{([^}]*)\}', replace_block, final_content,
                                           flags=re.DOTALL)
                else:
                    final_content += f'\n+ boot_menu {{\n  left = {left_val}\n  top = {top_val}\n  width = 50%\n  height = 40%\n}}\n'

        return final_content

    except Exception as e:
        print(f"Error preparing save: {e}")
        return None