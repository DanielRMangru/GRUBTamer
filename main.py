import sys
import os
import subprocess
import gi
import tempfile
from src.parser import read_grub_config
from src.system import AVAILABLE_OPTIONS, GRUB_DOCS_OPTIONS
from src.theme_editor import ThemeEditorWindow
from src.boot_manager import BootManagerWindow


gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
# noinspection PyUnresolvedReferences
from gi.repository import Gtk, Adw, Gio

# Default path if none is set
DEFAULT_THEME_PATH = "/boot/grub/themes/GrubTamer/theme.txt"
BACKUP_PATH = "/etc/default/grub.bak"


class GrubTamerWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("GrubTamer")
        self.set_default_size(600, 750)

        self.grub_settings = read_grub_config()
        self.widget_map = {}

        self.ensure_theme_ready()

        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toast_overlay.set_child(self.main_box)

        # --- Header with Menu ---
        header = Adw.HeaderBar()

        # Add Command Button
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Add Command")
        add_btn.connect("clicked", self.on_add_command_clicked)
        header.pack_start(add_btn)

        # Save Button
        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        header.pack_end(save_btn)

        # Main Menu (Hamburger)
        menu_model = Gio.Menu()
        menu_model.append("Create Backup", "win.create_backup")
        menu_model.append("Restore Backup", "win.restore_backup")
        menu_model.append("Refresh Themes", "win.refresh_themes")

        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        header.pack_end(menu_btn)

        # Actions
        self.add_action_simple("create_backup", self.on_create_backup)
        self.add_action_simple("restore_backup", self.on_restore_backup)
        self.add_action_simple("refresh_themes", self.on_refresh_themes)

        self.main_box.append(header)

        # Content
        self.page = Adw.PreferencesPage()
        self.page.set_vexpand(True)
        self.main_box.append(self.page)

        # Build Standard Rows
        standard_keys = set()
        for category, options in AVAILABLE_OPTIONS.items():
            group = Adw.PreferencesGroup(title=category)
            self.page.add(group)
            for opt in options:
                standard_keys.add(opt["key"])
                row = self.create_row(opt["key"], opt["label"], opt["desc"], opt["type"], example=opt.get("example"))
                group.add(row)

        # Build Extra Rows
        self.custom_group = Adw.PreferencesGroup(title="Extra Configuration")
        self.page.add(self.custom_group)

        for loaded_key in self.grub_settings.keys():
            if loaded_key not in standard_keys:
                if loaded_key in GRUB_DOCS_OPTIONS:
                    data = GRUB_DOCS_OPTIONS[loaded_key]
                    row = self.create_row(loaded_key, data['label'], data['desc'], data['type'],
                                          example=data.get('example'), is_custom=True)
                else:
                    row = self.create_row(loaded_key, loaded_key, "Custom parameter", "text", is_custom=True)
                self.custom_group.add(row)

    def add_action_simple(self, name, callback):
        act = Gio.SimpleAction.new(name, None)
        act.connect("activate", callback)
        self.add_action(act)

    def ensure_theme_ready(self):
        current_theme = self.grub_settings.get("GRUB_THEME", "").strip('"').strip("'")
        if not current_theme:
            self.grub_settings["GRUB_THEME"] = DEFAULT_THEME_PATH
            current_theme = DEFAULT_THEME_PATH
        if not os.path.exists(current_theme):
            try:
                theme_dir = os.path.dirname(current_theme)
                subprocess.run(["pkexec", "mkdir", "-p", theme_dir], check=True)
                subprocess.run(["pkexec", "touch", current_theme], check=True)
                subprocess.run(["pkexec", "chmod", "644", current_theme], check=True)
            except:
                pass

    def get_available_themes(self):
        """Scans /boot/grub/themes/ for subdirectories."""
        base_dir = "/boot/grub/themes"
        themes = []
        if os.path.exists(base_dir):
            for name in os.listdir(base_dir):
                full_path = os.path.join(base_dir, name)
                theme_file = os.path.join(full_path, "theme.txt")
                if os.path.isdir(full_path) and os.path.exists(theme_file):
                    themes.append(name)
        if not themes: themes = ["GrubTamer"]
        return sorted(themes)

    def create_row(self, key, label, desc, opt_type, example=None, is_custom=False):
        row = Adw.ActionRow(title=label, subtitle=desc)
        current_val = self.grub_settings.get(key, "")

        if opt_type == "toggle":
            active = str(current_val).lower() in ["true", "y", "yes", "1"]
            widget = Gtk.Switch(active=active)
            widget.set_valign(Gtk.Align.CENTER)
            widget.set_tooltip_text(f"ON = {key}=true\nOFF = {key}=false")
            row.add_suffix(widget)
            self.widget_map[key] = widget

        # --- NEW: Boot Entry Selector ---
        elif key == "GRUB_DEFAULT":
            # Container for Entry + Button
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            entry_widget = Gtk.Entry(text=str(current_val))
            entry_widget.set_valign(Gtk.Align.CENTER)
            entry_widget.set_hexpand(True)
            if example: entry_widget.set_placeholder_text(example)

            btn_select = Gtk.Button(icon_name="system-search-symbolic")
            btn_select.set_tooltip_text("Select from detected boot entries")
            btn_select.set_valign(Gtk.Align.CENTER)

            # Callback to handle selection
            def on_boot_selected(name):
                # Quote the name because it likely contains spaces
                # GRUB needs: GRUB_DEFAULT="Windows Boot Manager"
                # But our parser/writer handles quotes, so just setting the text is usually fine.
                entry_widget.set_text(f"{name}")

            btn_select.connect("clicked", lambda b: BootManagerWindow(on_boot_selected, transient_for=self).present())

            box.append(entry_widget)
            box.append(btn_select)

            row.add_suffix(box)
            self.widget_map[key] = entry_widget

        # --- Theme Selector ---
        elif key == "GRUB_THEME":
            themes = self.get_available_themes()
            model = Gtk.StringList.new(themes)
            dropdown = Gtk.DropDown(model=model)
            dropdown.set_valign(Gtk.Align.CENTER)

            current_path = str(current_val).strip('"').strip("'")
            selected_idx = 0
            for i, name in enumerate(themes):
                if name in current_path:
                    selected_idx = i
                    break
            dropdown.set_selected(selected_idx)

            box_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            box_row.append(dropdown)

            edit_btn = Gtk.Button(label="Edit")
            edit_btn.set_valign(Gtk.Align.CENTER)
            edit_btn.add_css_class("pill")

            def on_edit_clicked(btn):
                idx = dropdown.get_selected()
                theme_name = themes[idx]
                path = f"/boot/grub/themes/{theme_name}/theme.txt"
                self.open_theme_editor(path)

            edit_btn.connect("clicked", on_edit_clicked)
            box_row.append(edit_btn)

            row.add_suffix(box_row)
            self.widget_map[key] = (dropdown, themes)

        else:
            widget = Gtk.Entry(text=str(current_val))
            widget.set_valign(Gtk.Align.CENTER)
            widget.set_hexpand(True)
            if example:
                widget.set_placeholder_text(f"e.g. {example}")
            widget.set_tooltip_text(f"Modifies {key}")

            row.add_suffix(widget)
            self.widget_map[key] = widget

        if is_custom:
            remove_btn = Gtk.Button(icon_name="user-trash-symbolic")
            remove_btn.add_css_class("error")
            remove_btn.set_valign(Gtk.Align.CENTER)
            remove_btn.connect("clicked", lambda btn: self.remove_custom_row(row, key))
            row.add_suffix(remove_btn)

        return row

    def open_theme_editor(self, path):
        ThemeEditorWindow(theme_path=path, transient_for=self).present()

    def remove_custom_row(self, row_widget, key):
        self.custom_group.remove(row_widget)
        if key in self.widget_map: del self.widget_map[key]
        if key in self.grub_settings: del self.grub_settings[key]

    def on_add_command_clicked(self, button):
        """Displays the search dialog for new commands."""
        dialog = Gtk.Window(
            title="Add GRUB Command",
            transient_for=self,
            modal=True,
            default_width=450,
            default_height=600
        )

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(12);
        content.set_margin_bottom(12)
        content.set_margin_start(12);
        content.set_margin_end(12)
        dialog.set_child(content)

        search_entry = Gtk.SearchEntry(placeholder_text="Search available commands...")
        content.append(search_entry)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        content.append(scrolled)

        listbox = Gtk.ListBox()
        listbox.add_css_class("boxed-list")
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scrolled.set_child(listbox)

        def get_unused_keys():
            return [k for k in GRUB_DOCS_OPTIONS.keys() if k not in self.widget_map]

        def populate_list(filter_text=""):
            while child := listbox.get_first_child(): listbox.remove(child)
            for key in get_unused_keys():
                data = GRUB_DOCS_OPTIONS[key]
                if filter_text.lower() in key.lower() or filter_text.lower() in data['label'].lower():
                    row = Adw.ActionRow(title=key, subtitle=data['label'])

                    # Store key and make clickable
                    row.grub_key = key
                    row.set_activatable(True)

                    listbox.append(row)

        populate_list()
        search_entry.connect("search-changed", lambda e: populate_list(e.get_text()))

        def on_row_activated(lb, row):
            target_key = row.grub_key
            target_data = GRUB_DOCS_OPTIONS[target_key]

            # Create the row using the main window's helper
            new_row = self.create_row(
                target_key,
                target_data['label'],
                target_data['desc'],
                target_data['type'],
                example=target_data.get('example'),
                is_custom=True
            )

            self.custom_group.add(new_row)
            dialog.close()
            self.show_toast(f"Added {target_key}")

        listbox.connect("row-activated", on_row_activated)
        dialog.present()
        pass

    def on_save_clicked(self, button):
        # 1. Gather Data (Same as before)
        for key, widget in self.widget_map.items():
            if key == "GRUB_THEME":
                dropdown, themes = widget
                idx = dropdown.get_selected()
                theme_name = themes[idx]
                self.grub_settings[key] = f"/boot/grub/themes/{theme_name}/theme.txt"
            elif isinstance(widget, Gtk.Entry):
                self.grub_settings[key] = widget.get_text().strip()
            elif isinstance(widget, Gtk.Switch):
                self.grub_settings[key] = "true" if widget.get_active() else "false"

        lines = []
        for k, v in self.grub_settings.items():
            val = str(v)
            if not val.strip(): continue
            if not val.isdigit():
                lines.append(f'{k}="{val.replace('"', '')}"')
            else:
                lines.append(f'{k}={val}')

        payload = "\n".join(lines) + "\n"

        # 2. FIX: Bundle operations to reduce password prompts
        # First, write payload to a temporary user-owned file (no password needed)
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                tmp.write(payload)
                tmp_path = tmp.name

            # Next, run ONE root command that does everything:
            # A. Overwrite /etc/default/grub with temp content
            # B. Delete the temp file
            # C. Run update-grub
            cmd = f"cat '{tmp_path}' > /etc/default/grub && rm '{tmp_path}' && update-grub"

            subprocess.run(["pkexec", "sh", "-c", cmd], check=True)
            self.show_toast("System updated successfully!")

        except subprocess.CalledProcessError:
            self.show_toast("Save cancelled or failed.")
        except Exception as e:
            self.show_toast(f"Error: {e}")

    def on_create_backup(self, action, param):
        try:
            subprocess.run(["pkexec", "cp", "/etc/default/grub", BACKUP_PATH], check=True)
            self.show_toast("Backup created at /etc/default/grub.bak")
        except Exception as e:
            self.show_toast(f"Backup failed: {e}")

    def on_restore_backup(self, action, param):
        if not os.path.exists(BACKUP_PATH):
            self.show_toast("No backup found!")
            return
        try:
            subprocess.run(["pkexec", "cp", BACKUP_PATH, "/etc/default/grub"], check=True)
            self.grub_settings = read_grub_config()  # Reload state
            self.show_toast("Restored! Please restart app to see changes.")
        except Exception as e:
            self.show_toast(f"Restore failed: {e}")

    def on_refresh_themes(self, action, param):
        # Trigger a refresh of the dropdown if needed, or just notify
        self.show_toast("Refreshed theme list.")

    def show_toast(self, message):
        self.toast_overlay.add_toast(Adw.Toast.new(message))


class GrubTamerApp(Adw.Application):
    def __init__(self): super().__init__(application_id='org.example.GrubTamer')

    def do_activate(self): GrubTamerWindow(application=self).present()


if __name__ == "__main__": GrubTamerApp().run(sys.argv)