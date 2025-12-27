# GRUBTamer

GRUBTamer is a modern, GUI-based editor for managing and customizing the GRUB2 bootloader. Built with Python and GTK4/Libadwaita, it provides a user-friendly interface to configure boot settings, manage boot entries, and customize themes without manually editing configuration files.

## Features

*   **General Settings**: Easily adjust the default boot entry, timeout duration, and menu visibility.
*   **Kernel Parameters**: Add or remove kernel arguments safely.
*   **Theme Editor**: Customize the look and feel of your boot menu with a visual editor.
    *   Change background images and colors.
    *   Adjust fonts, menu positioning, and progress bar styles.
    *   Live preview of theme changes.
*   **Boot Entries**: View and manage detected operating systems and kernels.
*   **Backup & Restore**: Automatically backs up configuration files before saving changes.

## Requirements

*   Python 3
*   GTK4
*   Libadwaita
*   `grub-mkconfig` (standard on most Linux distributions)
*   `pkexec` (for privileged operations)

## Installation & Usage

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/GRUBTamer.git
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

## Attributions
*   **Developer:** Daniel R Mangru (concept, direction, debugger)
*   **Code Generation**: Portions of the code and logic were generated with the assistance of **Gemini 3 Pro** (Google).
*   **Reference Documentation**: Development was guided by the official [GNU GRUB Manual](https://www.gnu.org/software/grub/manual/grub/grub.html) and GTK4/Libadwaita documentation.

## License

[MIT License](LICENSE)
