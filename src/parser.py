import os
GRUB_PATH = "/etc/default/grub"

def read_grub_config():
    """Reads the GRUB config file and returns a dictionary of settings."""
    settings = {}
    try:
        with open(GRUB_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Clean up quotes from values
                    settings[key.strip()] = value.strip().strip('"').strip("'")
        return settings
    except FileNotFoundError:
        return {"error": "GRUB configuration file not found."}
    except PermissionError:
        return {"error": "Permission denied. Please run with elevated privileges."}

if __name__ == "__main__":
    # Quick test
    print(read_grub_config())

def save_grub_config(settings_dict):
    """Writes the dictionary back to /etc/default/grub."""
    try:
        # It's best practice to read the file first to preserve comments,
        # but for this iteration, we will write a clean key-value file.
        with open(GRUB_PATH, 'w') as f:
            for key, value in settings_dict.items():
                # Ensure values with spaces are quoted
                if " " in str(value) or not str(value).isdigit():
                    f.write(f'{key}="{value}"\n')
                else:
                    f.write(f'{key}={value}\n')
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False