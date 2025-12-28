import os
import re

# Expanded Global Properties
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

    # --- GROUP: Boot Menu Styling ---
    "box-border-color": {
        "label": "Box Border / Normal Text",
        "type": "color",
        "group": "Boot Menu Styling",
        "desc": "Color of the border (and non-highlighted text).",
        "virtual": False
    },
    "box-bg-color": {
        "label": "Box Background",
        "type": "color",
        "group": "Boot Menu Styling",
        "desc": "Background color of the menu box (Supports Transparency).",
        "virtual": False
    },
    "selected-item-color": {
        "label": "Selected Item Text",
        "type": "color",
        "group": "Boot Menu Styling",
        "desc": "Text color of the highlighted entry.",
        "virtual": True
    },

    # --- GROUP: Footer Text ---
    "message-font": {"label": "Message Font", "type": "font", "group": "Footer Text",
                     "desc": "Font used for footer messages."},
    "message-color": {"label": "Message Color", "type": "color", "group": "Footer Text",
                      "desc": "Color of the message text."},

    # --- GROUP: Progress Bar ---
    "progress-style": {
        "label": "Progress Style",
        "type": "dropdown",
        "group": "Progress Bar",
        "options": ["bar", "circle"],  # Re-enabled circle
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

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'): continue
            match = re.match(r'^([\w\-]+)\s*:\s*"?([^"]*)"?', line)
            if match:
                key = match.group(1)
                val = match.group(2)
                if key in THEME_GLOBALS:
                    properties[key] = val

        # Parse Blocks (Progress / Menu)

        # Check for CIRCULAR first
        cp_match = re.search(r'\+\s*circular_progress\s*\{(.*?)\}', content, re.DOTALL)
        if cp_match:
            properties["progress-style"] = "circle"
            # We don't easily parse colors from images, so we might default or try to read globals if we saved them elsewhere
            # For simplicity, we assume the user sets them in the UI.

        # Check for BAR second (overwrite if found, though usually mutually exclusive)
        pb_match = re.search(r'\+\s*progress_bar\s*\{(.*?)\}', content, re.DOTALL)
        if pb_match:
            block = pb_match.group(1)
            if m := re.search(r'fg_color\s*=\s*"?([^"\n]*)"?', block): properties["progress-color"] = m.group(1)
            if m := re.search(r'bg_color\s*=\s*"?([^"\n]*)"?', block): properties["progress-bg-color"] = m.group(1)
            properties["progress-style"] = "bar"

        bm_match = re.search(r'\+\s*boot_menu\s*\{(.*?)\}', content, re.DOTALL)
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
            if m := re.search(r'item_color\s*=\s*"?([^"\n]*)"?', block):
                properties["box-border-color"] = m.group(1)
            if m := re.search(r'selected_item_color\s*=\s*"?([^"\n]*)"?', block):
                properties["selected-item-color"] = m.group(1)

    except Exception as e:
        print(f"Error parsing theme: {e}")
    return properties


def save_theme(theme_path, data_dict):
    if not os.path.exists(theme_path): return None

    try:
        with open(theme_path, 'r') as f:
            content = f.read()

        # 1. Prepare Block Content

        # PROGRESS LOGIC
        style = data_dict.get("progress-style", "bar")
        p_color = data_dict.get("progress-color", "#ffffff")
        p_bg = data_dict.get("progress-bg-color", "#333333")

        new_progress_block = ""

        if style == "circle":
            # Circular Progress Block
            # Relies on generated assets: c_center.png (bg) and c_tick.png (fg)
            new_progress_block = f"""
+ circular_progress {{
    id = "__timeout__"
    left = 50%
    top = 90%
    width = 60
    height = 60
    center_bitmap = "c_center.png"
    tick_bitmap = "c_tick.png"
    num_ticks = 100
    start_angle = 0
    ticks_disappear = false
}}
"""
        else:
            # Standard Bar Block
            new_progress_block = f"""
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

        left_val, top_val = "25%", "30%"
        if "menu-position" in data_dict and data_dict["menu-position"] in POSITION_MAP:
            left_val, top_val = POSITION_MAP[data_dict["menu-position"]]

        normal_color = data_dict.get("box-border-color", "#ffffff")
        sel_color = data_dict.get("selected-item-color", "#000000")

        new_boot_menu = f"""
+ boot_menu {{
    left = {left_val}
    top = {top_val}
    width = 50%
    height = 40%
    item_color = "{normal_color}"
    selected_item_color = "{sel_color}"
    menu_pixmap_style = "menu_*.png"
    item_height = 30
    item_spacing = 10
    icon_width = 32
    icon_height = 32
}}
"""

        # 2. Rebuild File
        lines = content.splitlines()
        new_lines = []
        processed_keys = set()

        for line in lines:
            stripped = line.strip()
            match = re.match(r'^([\w\-]+)\s*:\s*"?([^"]*)"?', stripped)
            if match and not stripped.startswith('#') and '{' not in stripped:
                key = match.group(1)
                if key in data_dict and key in THEME_GLOBALS and not THEME_GLOBALS[key].get("virtual"):
                    new_lines.append(f'{key}: "{data_dict[key]}"')
                    processed_keys.add(key)
                elif key in THEME_GLOBALS and THEME_GLOBALS[key].get("virtual"):
                    pass
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        for key, val in data_dict.items():
            if key in THEME_GLOBALS and not THEME_GLOBALS[key].get("virtual"):
                if key not in processed_keys: new_lines.append(f'{key}: "{val}"')

        final_content = "\n".join(new_lines) + "\n"

        # 3. Replace Blocks
        # Remove BOTH types of progress blocks to be safe
        final_content = re.sub(r'\+\s*progress_bar\s*\{(.*?)\}', '', final_content, flags=re.DOTALL)
        final_content = re.sub(r'\+\s*circular_progress\s*\{(.*?)\}', '', final_content, flags=re.DOTALL)

        final_content = re.sub(r'\+\s*boot_menu\s*\{(.*?)\}', '', final_content, flags=re.DOTALL)

        final_content = final_content.strip() + "\n\n"

        final_content += new_boot_menu
        final_content += new_progress_block

        return final_content

    except Exception as e:
        print(f"Error preparing save: {e}")
        return None