import re
import subprocess
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


def get_boot_entries():
    """Parses /boot/grub/grub.cfg using pkexec to bypass permission issues."""
    entries = []
    cfg_path = '/boot/grub/grub.cfg'

    try:
        # FIX: Use pkexec cat instead of open() to read root-owned file
        # This will trigger a password prompt if the user hasn't authenticated recently
        result = subprocess.run(
            ["pkexec", "cat", cfg_path],
            capture_output=True,
            text=True,
            check=True
        )
        content = result.stdout

        for line in content.splitlines():
            # Look for lines starting with: menuentry 'Title' ...
            # Regex handles both single (' ') and double (" ") quotes
            match = re.search(r"^\s*menuentry\s+['\"]([^'\"]+)['\"]", line)
            if match:
                title = match.group(1)
                entries.append(title)

    except subprocess.CalledProcessError:
        # Occurs if user hits Cancel on password prompt
        return ["Authentication cancelled"]
    except Exception as e:
        print(f"Error reading boot entries: {e}")
        return [f"Error: {e}"]

    if not entries:
        return ["No entries found (Is GRUB installed?)"]

    return entries


class BootManagerWindow(Adw.Window):
    def __init__(self, on_select_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_select_callback = on_select_callback

        self.set_title("Select Default Boot Entry")
        self.set_default_size(500, 600)
        self.set_modal(True)

        # UI Shell
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        # Header
        header = Adw.HeaderBar()
        box.append(header)

        # Explanation
        info_row = Adw.ActionRow(title="Select the OS to boot by default",
                                 subtitle="This sets GRUB_DEFAULT to the exact name, which is safer than using numbers.")
        info_row.set_selectable(False)

        # List Group
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup()
        group.add(info_row)

        # Populate List
        entries = get_boot_entries()
        for entry in entries:
            row = Adw.ActionRow(title=entry)

            # Selection Button
            btn = Gtk.Button(label="Select")
            btn.set_valign(Gtk.Align.CENTER)
            btn.add_css_class("pill")

            # Connect click
            # If extraction failed (e.g. "Authentication cancelled"), disable the button
            if entry.startswith("Error") or entry.startswith("Auth") or entry.startswith("No entries"):
                btn.set_sensitive(False)

            btn.connect("clicked", self.on_entry_clicked, entry)

            row.add_suffix(btn)
            group.add(row)

        page.add(group)

        # Scrollable container
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(page)
        scrolled.set_vexpand(True)
        box.append(scrolled)

    def on_entry_clicked(self, button, entry_name):
        self.on_select_callback(entry_name)
        self.close()