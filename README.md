# GRUBTamer

GRUBTamer is a modern, GUI-based editor for managing and customizing the GRUB2 bootloader. Built with Python and GTK4/Libadwaita, it provides a user-friendly interface to configure boot settings, manage boot entries, and customize themes without manually editing configuration files.

## Why?
I wanted to edit my GRUB menu and make some customizations to the loading screen. This one is Linux based.

## Features

*   **General Settings**: Easily adjust the default boot entry, timeout duration, and menu visibility.
*   **Kernel Parameters**: Add or remove kernel arguments safely.
*   **Theme Editor**: Customize the look and feel of your boot menu with a visual editor.
    *   Change background images and colors.
    *   Adjust fonts, menu positioning, and progress bar styles.
    *   Live preview of theme changes.
*   **Boot Entries**: View and manage detected operating systems and kernels.
*   **Backup & Restore**: Automatically backs up configuration files before saving changes.

<img width="381" height="481" alt="Screenshot from 2025-12-27 12-24-36" src="https://github.com/user-attachments/assets/1a380ab4-5442-4d85-93a7-2eac725e2007" />

<img width="381" height="481" alt="Screenshot from 2025-12-27 12-24-57" src="https://github.com/user-attachments/assets/25506c29-cce8-49ff-966b-e16c56a64560" />

<img width="381" height="481" alt="Screenshot from 2025-12-27 12-25-50" src="https://github.com/user-attachments/assets/df88c3e1-8954-491a-9335-e3361dae8694" />

<img width="381" height="481" alt="Screenshot from 2025-12-27 12-25-58" src="https://github.com/user-attachments/assets/b5453d78-0d23-4bbf-be84-9418aa66f411" />

<img width="681" height="514" alt="Screenshot from 2025-12-27 12-26-57" src="https://github.com/user-attachments/assets/686b0e17-2bb9-4002-98f3-27888608377e" />

## Requirements

*   Python 3
*   GTK4
*   Libadwaita
*   `grub-mkconfig` (standard on most Linux distributions)
*   `pkexec` (for privileged operations)

## Installation & Usage

1.  Clone the repository:
    ```bash
    git clone https://github.com/DanielRMangru/GRUBTamer.git
    cd GRUBTamer
    ```

2.  Install dependencies (example for Debian/Ubuntu):
    ```bash
    sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
    ```
    > **Note:** If a theme file does not exist, the application will ask for elevated privileges to write a default one before the full interface appears.

3.  Run the application:
    ```bash
    python3 main.py
    ```
## Change Log
Changelog - GrubTamer Project
Date: 2025-12-27

[v1.1.0] - Packaging & Deployment
- Added install.sh script for automated dependency installation (apt) and file deployment (/opt/grubtamer).
- Added .desktop file generation for system menu integration.
- Added icon.png and integrated it into the installer.
- Created requirements.txt for Python package tracking.
- Removed redundant 'GRUB_BACKGROUND' option from main UI (src/system.py).

[v1.0.5] - Boot Entry Management
- Implemented src/boot_manager.py to parse /boot/grub/grub.cfg.
- Added UI to "Default Entry" row to select boot targets by name instead of index.
- Fixed permission issues by reading grub.cfg via `pkexec cat`.

[v1.0.4] - Theme Editor Transaction Safety
- Refactored on_save_clicked in ThemeEditorWindow to bundle all operations (Asset Move + File Write) into a single `pkexec` transaction.
- Eliminated multiple password prompts during save.
- Fixed accumulating whitespace issue in theme.txt parser.

[v1.0.3] - Dynamic Asset Generation
- Implemented GdkPixbuf logic to generate 1x1 PNGs for Menu Box backgrounds (enabling transparency support).
- Implemented Cairo logic to generate dynamic assets (ring/dot) for Circular Progress indicators.
- Updated src/theme_parser.py to link `menu_pixmap_style` and `circular_progress` blocks to generated assets.

[v1.0.2] - Parser & Styling Fixes
- Fixed critical bug where internal GUI keys (e.g., progress-style) were corrupting theme.txt syntax.
- Implemented 'virtual' property flags in parser to separate UI state from GRUB config.
- Fixed missing colors in Boot Menu by explicitly mapping `item_color` and `selected_item_color`.
- Split "Styled Box" UI group into "Boot Menu Styling" and "Footer Text" for clarity.

[v1.0.1] - Permissions & GTK Fixes
- Replaced deprecated `set_margin_all` with individual margin setters for GTK4 compliance.
- Fixed `AttributeError` in secondary windows by implementing `Gio.SimpleActionGroup`.
- Implemented automatic asset import logic: dragging/selecting files now copies them to the theme directory via `pkexec` to ensure GRUB visibility.

[v1.0.0] - Initial Commit
- Basic functionality for editing /etc/default/grub.
- Initial Theme Editor UI.

## Attributions
*   **Developer:** Daniel R Mangru (concept, direction, debugger)
*   **Code Generation**: Portions of the code and logic were generated with the assistance of **Gemini 3 Pro** (Google).
*   **Reference Documentation**: Development was guided by the official [GNU GRUB Manual](https://www.gnu.org/software/grub/manual/grub/grub.html) and GTK4/Libadwaita documentation.

## License

[MIT License](LICENSE)
