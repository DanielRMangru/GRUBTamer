AVAILABLE_OPTIONS = {
    "General": [
        {
            "key": "GRUB_DEFAULT",
            "label": "Default Entry",
            "desc": "The numeric index (0) or full name of the entry to boot by default.",
            "type": "text",
            "example": "0"
        },
        {
            "key": "GRUB_TIMEOUT",
            "label": "Timeout",
            "desc": "Seconds to wait before booting. Set to -1 to wait indefinitely.",
            "type": "text",
            "example": "5"
        },
        {
            "key": "GRUB_DISTRIBUTOR",
            "label": "Distributor Name",
            "desc": "The name displayed in the menu entries (e.g., Ubuntu, Arch).",
            "type": "text",
            "example": "Ubuntu"
        },
    ],
    "Appearance": [
        {
            "key": "GRUB_THEME",
            "label": "Theme Path",
            "desc": "Full path to a text-based or graphical theme file (.txt).",
            "type": "file",
            "example": "/boot/grub/themes/starfield/theme.txt"
        },
        {
            "key": "GRUB_BACKGROUND",
            "label": "Background Image",
            "desc": "Full path to a PNG/JPG image (must be readable by GRUB).",
            "type": "file",
            "example": "/usr/share/backgrounds/warty-final-ubuntu.png"
        },
    ],
    "Advanced": [
        {
            "key": "GRUB_CMDLINE_LINUX_DEFAULT",
            "label": "Kernel Params (Default)",
            "desc": "Arguments passed to the kernel for normal boots (e.g., quiet splash).",
            "type": "text",
            "example": "quiet splash"
        },
        {
            "key": "GRUB_CMDLINE_LINUX",
            "label": "Kernel Params (All)",
            "desc": "Arguments passed to ALL kernel entries (recovery included).",
            "type": "text",
            "example": "console=ttyS0"
        },
        {
            "key": "GRUB_DISABLE_OS_PROBER",
            "label": "Disable OS Prober",
            "desc": "If enabled (ON), GRUB will NOT look for Windows or other OS installs.",
            "type": "toggle",
            "example": "true"
        },
    ]
}

GRUB_DOCS_OPTIONS = {
    "GRUB_GFXMODE": {
        "label": "Resolution",
        "type": "text",
        "desc": "Screen resolution for the menu. Must be supported by VBE.",
        "example": "1920x1080"
    },
    "GRUB_DISABLE_RECOVERY": {
        "label": "Disable Recovery",
        "type": "toggle",
        "desc": "If enabled (ON), recovery mode entries will be hidden from the menu.",
        "example": "true"
    },
    "GRUB_INIT_TUNE": {
        "label": "Beep on Boot",
        "type": "text",
        "desc": "Play a tone on startup. Format: 'tempo freq dur'.",
        "example": "480 440 1"
    },
    "GRUB_TERMINAL_OUTPUT": {
        "label": "Terminal Output",
        "type": "text",
        "desc": "The output backend. Use 'console' for text-only or 'gfxterm' for graphics.",
        "example": "gfxterm"
    },
     "GRUB_DISABLE_SUBMENU": {
        "label": "Disable Submenus",
        "type": "toggle",
        "desc": "If enabled (ON), all kernels are shown in the main menu instead of a folder.",
        "example": "true"
    }
}