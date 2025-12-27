import subprocess
import os
import gi
from src.theme_parser import parse_theme, save_theme, THEME_GLOBALS

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
# noinspection PyUnresolvedReferences
from gi.repository import Gtk, Adw, Gdk, Pango, Gio, GLib


# --- PREVIEW WINDOW ---
class ThemePreviewWindow(Gtk.Window):
    def __init__(self, theme_data):
        super().__init__(title="Theme Preview")
        self.set_default_size(900, 650)
        self.set_modal(True)

        overlay = Gtk.Overlay()
        self.set_child(overlay)

        # 1. Background Layer
        bg_image = theme_data.get('desktop-image', '').strip('"')
        bg_color = theme_data.get('desktop-color', '#333333').strip('"')

        pic = Gtk.Picture()
        pic.set_content_fit(Gtk.ContentFit.COVER)
        if bg_image and os.path.exists(bg_image):
            pic.set_file(Gio.File.new_for_path(bg_image))
        else:
            self.apply_css(pic, f"picture {{ background-color: {bg_color}; }}")
        overlay.set_child(pic)

        # 2. Boot Menu Layer
        pos_name = theme_data.get('menu-position', 'Center')
        halign, valign = Gtk.Align.CENTER, Gtk.Align.CENTER
        if "North" in pos_name:
            valign = Gtk.Align.START
        elif "South" in pos_name:
            valign = Gtk.Align.END
        if "West" in pos_name:
            halign = Gtk.Align.START
        elif "East" in pos_name:
            halign = Gtk.Align.END

        menu_frame = Gtk.Frame()
        menu_frame.set_halign(halign)
        menu_frame.set_valign(valign)

        # FIX: Explicit margins
        menu_frame.set_margin_top(50)
        menu_frame.set_margin_bottom(50)
        menu_frame.set_margin_start(50)
        menu_frame.set_margin_end(50)

        menu_frame.set_size_request(350, 200)

        overlay.add_overlay(menu_frame)

        box_bg = theme_data.get('box-bg-color', 'rgba(0,0,0,0.5)').strip('"')
        box_border = theme_data.get('box-border-color', 'white').strip('"')
        self.apply_css(menu_frame,
                       f"frame {{ background-color: {box_bg}; border: 2px solid {box_border}; border-radius: 6px; }}")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # FIX: Explicit margins for the box content
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)

        menu_frame.set_child(vbox)

        title_text = theme_data.get('title-text', 'GNU GRUB version 2.06').strip('"')
        title_color = theme_data.get('title-color', 'white').strip('"')
        lbl_title = Gtk.Label(label=title_text)
        lbl_title.add_css_class("title-2")
        self.apply_css(lbl_title, f"label {{ color: {title_color}; font-weight: bold; margin-bottom: 10px; }}")
        vbox.append(lbl_title)

        sel_txt = theme_data.get('selected-item-color', 'white').strip('"')
        sel_bg = theme_data.get('selected-item-bg-color', '#4a90d9').strip('"')

        items = ["Ubuntu", "Advanced options for Ubuntu", "Windows Boot Manager", "UEFI Firmware Settings"]
        for i, item in enumerate(items):
            item_lbl = Gtk.Label(label=item)
            item_lbl.set_xalign(0.0)

            # FIX: Explicit margins for items
            item_lbl.set_margin_start(10)
            item_lbl.set_margin_end(10)
            item_lbl.set_margin_top(4)
            item_lbl.set_margin_bottom(4)

            if i == 0:
                self.apply_css(item_lbl,
                               f"label {{ background-color: {sel_bg}; color: {sel_txt}; border-radius: 3px; }}")
            else:
                self.apply_css(item_lbl, f"label {{ color: {box_border}; }}")
            vbox.append(item_lbl)

        # 3. Footer Layer
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        footer_box.set_valign(Gtk.Align.END);
        footer_box.set_halign(Gtk.Align.CENTER)
        footer_box.set_margin_bottom(40)
        overlay.add_overlay(footer_box)

        prog_style = theme_data.get('progress-style', 'bar').strip('"').lower()
        prog_color = theme_data.get('progress-color', 'white').strip('"')
        prog_bg = theme_data.get('progress-bg-color', 'grey').strip('"')

        if prog_style == 'circle':
            box_spin = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box_spin.set_halign(Gtk.Align.CENTER)
            spinner = Gtk.Spinner();
            spinner.set_size_request(32, 32);
            spinner.start()
            box_spin.append(spinner)
            lbl = Gtk.Label(label="Booting in 5s...");
            self.apply_css(lbl, f"label {{ color: {prog_color}; }}")
            box_spin.append(lbl)
            footer_box.append(box_spin)
        else:
            pbar = Gtk.ProgressBar();
            pbar.set_fraction(0.6);
            pbar.set_size_request(400, 20)
            self.apply_css(pbar,
                           f"progressbar trough {{ background-color: {prog_bg}; min-height: 8px; }} progressbar progress {{ background-color: {prog_color}; min-height: 8px; }}")
            footer_box.append(pbar)

        msg_color = theme_data.get('message-color', '#cccccc').strip('"')
        lbl_msg = Gtk.Label(label="Use the ↑ and ↓ keys to select an entry. Press Enter to boot.")
        self.apply_css(lbl_msg, f"label {{ color: {msg_color}; font-size: 14px; }}")
        footer_box.append(lbl_msg)

    @staticmethod
    def apply_css(widget, css):
        p = Gtk.CssProvider();
        p.load_from_data(css.encode())
        widget.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


# --- MAIN EDITOR WINDOW ---
class ThemeEditorWindow(Adw.Window):
    def __init__(self, theme_path, **kwargs):
        super().__init__(**kwargs)
        self.theme_path = theme_path
        self.set_title("Edit Theme")
        self.set_default_size(600, 850)
        self.set_modal(True)

        self.current_data = parse_theme(self.theme_path)
        self.widget_map = {}

        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toast_overlay.set_child(box)

        # --- Header with Menu ---
        header = Adw.HeaderBar()

        # Preview
        preview_btn = Gtk.Button(icon_name="eye-open-symbolic")
        preview_btn.set_tooltip_text("Preview Layout")
        preview_btn.connect("clicked", self.on_preview_clicked)
        header.pack_start(preview_btn)

        # Save
        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        header.pack_end(save_btn)

        # Menu (Hamburger)
        menu_model = Gio.Menu()
        menu_model.append("Save Copy As...", "win.save_as")
        menu_model.append("Reset to Defaults", "win.reset_defaults")

        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        header.pack_end(menu_btn)

        # Actions Group
        action_group = Gio.SimpleActionGroup()
        self.insert_action_group("win", action_group)

        act_save_as = Gio.SimpleAction.new("save_as", None)
        act_save_as.connect("activate", self.on_save_as_clicked)
        action_group.add_action(act_save_as)

        act_reset = Gio.SimpleAction.new("reset_defaults", None)
        act_reset.connect("activate", self.on_reset_clicked)
        action_group.add_action(act_reset)

        box.append(header)

        # Scrollable Content
        page = Adw.PreferencesPage()
        box.append(page)

        # Groups Setup
        groups_order = ["General", "Appearance", "Menu Layout", "Styled Box", "Progress Bar"]
        group_widgets = {}
        for g_name in groups_order:
            pg = Adw.PreferencesGroup(title=g_name)
            page.add(pg)
            group_widgets[g_name] = pg

        # Build Rows
        for key, meta in THEME_GLOBALS.items():
            group_name = meta.get("group", "General")
            target_group = group_widgets.get(group_name)
            if not target_group:
                target_group = Adw.PreferencesGroup(title=group_name)
                page.add(target_group)
                group_widgets[group_name] = target_group

            row = Adw.ActionRow(title=meta['label'], subtitle=meta.get('desc', ''))
            val = self.current_data.get(key, "")
            w_type = meta.get('type', 'text')

            # Factory logic
            if w_type == 'dropdown':
                options = meta.get('options', [])
                model = Gtk.StringList.new(options)
                dropdown = Gtk.DropDown(model=model)
                if val in options:
                    dropdown.set_selected(options.index(val))
                elif not val and options:
                    if "Center" in options: dropdown.set_selected(options.index("Center"))
                dropdown.set_valign(Gtk.Align.CENTER)
                self.widget_map[key] = {'type': 'dropdown', 'widget': dropdown, 'options': options}
                row.add_suffix(dropdown)
            elif w_type == 'color':
                rgba = Gdk.RGBA()
                if not rgba.parse(val): rgba.parse("white")
                widget = Gtk.ColorDialogButton()
                widget.set_dialog(Gtk.ColorDialog())
                widget.set_rgba(rgba);
                widget.set_valign(Gtk.Align.CENTER)
                self.widget_map[key] = {'type': 'color', 'widget': widget}
                row.add_suffix(widget)
            elif w_type == 'font':
                widget = Gtk.FontDialogButton();
                widget.set_dialog(Gtk.FontDialog())
                if val:
                    try:
                        widget.set_font_desc(Pango.FontDescription.from_string(val))
                    except:
                        pass
                widget.set_valign(Gtk.Align.CENTER)
                self.widget_map[key] = {'type': 'font', 'widget': widget}
                row.add_suffix(widget)
            elif w_type == 'file':
                entry = Gtk.Entry(text=val);
                entry.set_valign(Gtk.Align.CENTER);
                entry.set_hexpand(True)
                entry.set_placeholder_text("Select image...")
                box_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                box_row.append(entry)
                btn_browse = Gtk.Button(icon_name="folder-open-symbolic")
                btn_browse.set_valign(Gtk.Align.CENTER)
                btn_browse.connect("clicked", lambda b, e=entry: self.open_file_dialog(e))
                box_row.append(btn_browse)
                self.widget_map[key] = {'type': 'text', 'widget': entry}
                row.add_suffix(box_row)
            else:
                entry = Gtk.Entry(text=val);
                entry.set_valign(Gtk.Align.CENTER);
                entry.set_hexpand(True)
                self.widget_map[key] = {'type': 'text', 'widget': entry}
                row.add_suffix(entry)
            target_group.add(row)

    def open_file_dialog(self, entry_widget):
        d = Gtk.FileDialog()
        f = Gtk.FileFilter();
        f.add_mime_type("image/*");
        f.set_name("Images")
        filters = Gio.ListStore.new(Gtk.FileFilter);
        filters.append(f)
        d.set_filters(filters)
        d.open(self, None, self.on_file_dialog_finish, entry_widget)

    def on_file_dialog_finish(self, dialog, result, entry_widget):
        try:
            file = dialog.open_finish(result)
            if not file: return

            source_path = file.get_path()
            theme_dir = os.path.dirname(self.theme_path)

            # --- ASSET IMPORT LOGIC ---
            # 1. Check if the file is already inside the theme directory
            if os.path.commonpath([source_path, theme_dir]) == theme_dir:
                entry_widget.set_text(source_path)
            else:
                # 2. Copy external file to theme dir
                filename = os.path.basename(source_path)
                dest_path = os.path.join(theme_dir, filename)

                try:
                    subprocess.run(["pkexec", "cp", source_path, dest_path], check=True)
                    subprocess.run(["pkexec", "chmod", "644", dest_path], check=True)

                    self.show_toast(f"Imported image to {dest_path}")
                    entry_widget.set_text(dest_path)
                except Exception as e:
                    self.show_toast(f"Failed to import asset: {e}")
                    entry_widget.set_text(source_path)

        except Exception as e:
            print(f"File dialog error: {e}")

    def get_current_values(self):
        data = {}
        for key, meta in self.widget_map.items():
            w_type = meta['type']
            widget = meta['widget']
            val = ""
            if w_type == 'text':
                val = widget.get_text().strip()
            elif w_type == 'dropdown':
                idx = widget.get_selected()
                val = meta['options'][idx]
            elif w_type == 'color':
                rgba = widget.get_rgba()
                val = f"#{int(rgba.red * 255):02x}{int(rgba.green * 255):02x}{int(rgba.blue * 255):02x}"
            elif w_type == 'font':
                if desc := widget.get_font_desc(): val = desc.to_string()
            if val: data[key] = val
        return data

    def on_preview_clicked(self, _):
        ThemePreviewWindow(self.get_current_values()).present()

    def on_reset_clicked(self, action, param):
        defaults = {
            "menu-position": "Center",
            "box-bg-color": "#000000",
            "box-border-color": "#ffffff",
            "title-color": "#ffffff",
            "desktop-color": "#000000"
        }
        for key, val in defaults.items():
            if key in self.widget_map:
                meta = self.widget_map[key]
                if meta['type'] == 'text':
                    meta['widget'].set_text(val)
                elif meta['type'] == 'dropdown':
                    if val in meta['options']: meta['widget'].set_selected(meta['options'].index(val))
                elif meta['type'] == 'color':
                    rgba = Gdk.RGBA();
                    rgba.parse(val)
                    meta['widget'].set_rgba(rgba)
        self.show_toast("Reset to safe defaults (Save to apply).")

    def on_save_as_clicked(self, action, param):
        dialog = Gtk.Window(title="Save Theme As", transient_for=self, modal=True, default_width=300)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # FIX: Explicit margins for dialog box
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)

        dialog.set_child(vbox)

        lbl = Gtk.Label(label="Enter new theme folder name:")
        vbox.append(lbl)
        entry = Gtk.Entry(placeholder_text="MyNewTheme")
        vbox.append(entry)

        btn = Gtk.Button(label="Create & Save")
        btn.add_css_class("suggested-action")
        vbox.append(btn)

        def on_confirm(_):
            name = entry.get_text().strip()
            if not name: return
            new_dir = f"/boot/grub/themes/{name}"
            new_file = f"{new_dir}/theme.txt"
            try:
                subprocess.run(["pkexec", "mkdir", "-p", new_dir], check=True)
                content = save_theme(new_file, self.get_current_values())
                subprocess.run(["pkexec", "tee", new_file], input=content, text=True, check=True, capture_output=True)
                self.show_toast(f"Theme saved to {name}!")
                dialog.destroy()
            except Exception as e:
                self.show_toast(f"Error: {e}")

        btn.connect("clicked", on_confirm)
        dialog.present()

    def on_save_clicked(self, _):
        content = save_theme(self.theme_path, self.get_current_values())
        if not content: return
        try:
            subprocess.run(["pkexec", "tee", self.theme_path], input=content, text=True, check=True,
                           capture_output=True)
            self.show_toast("Theme saved successfully!")
        except Exception as e:
            self.show_toast(f"Error: {e}")

    def show_toast(self, msg):
        self.toast_overlay.add_toast(Adw.Toast.new(msg))