# Defines the standard GRUB parameters shown in the main window.
AVAILABLE_OPTIONS = {
    "General": [
        {"key": "GRUB_DEFAULT", "label": "Default Entry", "desc": "The numeric index (0) or full name of the entry to boot by default.", "type": "text", "example": "0"},
        {"key": "GRUB_TIMEOUT", "label": "Timeout", "desc": "Seconds to wait before booting. Set to -1 to wait indefinitely.", "type": "text", "example": "5"},
        {"key": "GRUB_DISTRIBUTOR", "label": "Distributor Name", "desc": "The name displayed in the menu entries (e.g., Ubuntu, Arch).", "type": "text", "example": "`lsb_release -i -s 2> /dev/null || echo Debian`"},
    ],
    "Appearance": [
        {"key": "GRUB_THEME", "label": "Theme Path", "desc": "Full path to a text-based or graphical theme file (.txt).", "type": "text", "example": "/boot/grub/themes/starfield/theme.txt"},
        # "GRUB_BACKGROUND" removed as it is redundant with the Theme Editor.
    ],
    "Advanced": [
        {"key": "GRUB_CMDLINE_LINUX_DEFAULT", "label": "Kernel Params (Default)", "desc": "Arguments passed to the kernel for normal boots (e.g., quiet splash).", "type": "text", "example": "quiet splash"},
        {"key": "GRUB_CMDLINE_LINUX", "label": "Kernel Params (All)", "desc": "Arguments passed to ALL kernel entries (recovery included).", "type": "text", "example": "console=ttyS0"},
        {"key": "GRUB_DISABLE_OS_PROBER", "label": "Disable OS Prober", "desc": "If enabled (ON), GRUB will NOT look for Windows or other OS installs.", "type": "toggle", "example": "true"},
    ]
}

# (The rest of the file remains unchanged)
# A larger list of known GRUB keys for the "Add Command" feature.
GRUB_DOCS_OPTIONS = {
    "GRUB_SAVEDEFAULT": {"label": "Save Default Entry", "desc": "If set to 'true', the last selected entry will be saved as the new default.", "type": "toggle"},
    "GRUB_TIMEOUT_STYLE": {"label": "Timeout Style", "desc": "'menu' to show the menu, 'countdown' to show a timer, 'hidden' to wait silently.", "type": "text", "example": "menu"},
    "GRUB_TERMINAL_OUTPUT": {"label": "Terminal Output", "desc": "The terminal device to use for output (e.g., 'gfxterm', 'console').", "type": "text", "example": "gfxterm"},
    "GRUB_GFXMODE": {"label": "Graphics Mode", "desc": "Resolution for graphical terminal (e.g., '1920x1080', 'auto').", "type": "text", "example": "auto"},
    "GRUB_DISABLE_RECOVERY": {"label": "Disable Recovery", "desc": "If set to 'true', recovery mode entries will not be generated.", "type": "toggle"},
    "GRUB_INIT_TUNE": {"label": "Init Tune", "desc": "Play a tune when GRUB starts.", "type": "text", "example": "480 440 1"},
    "GRUB_BADRAM": {"label": "Bad RAM Regions", "desc": "A list of memory regions to avoid using.", "type": "text", "example": "0x01234567,0xfedcba98"},
}