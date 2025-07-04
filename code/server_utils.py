import os
import re
import socket

def _find_steam_installations():
    paths = []
    # Common Steam installation paths
    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    if program_files_x86:
        potential_path = os.path.join(program_files_x86, "Steam")
        if os.path.exists(potential_path):
            paths.append(potential_path)

    program_files = os.environ.get("ProgramFiles")
    if program_files and program_files_x86 != program_files: # Avoid duplicating if ProgramFiles(x86) is same as ProgramFiles
        potential_path = os.path.join(program_files, "Steam")
        if os.path.exists(potential_path):
            paths.append(potential_path)
    
    # Check specific drive letters and common Program Files locations
    drive_letters = ['C', 'D', 'E', 'F']
    install_folders = ["Steam", "Program Files\\Steam", "Program Files (x86)\\Steam"]

    for drive in drive_letters:
        for folder in install_folders:
            potential_path = os.path.join(f"{drive}:\\", folder)
            if os.path.exists(potential_path):
                paths.append(potential_path)

    return list(set(paths)) # Return unique paths

def _parse_library_folders_vdf(vdf_path, log_callback=None):
    library_paths = []
    try:
        with open(vdf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Regex to find "path" values within numerical sections (library folders)
        paths_found = re.findall(r'"\d+"\s*{\s*"path"\s*"(.*?)"', content, re.DOTALL)
        for p in paths_found:
            # Normalize paths: replace double backslashes with single, forward slashes with os.sep
            cleaned_path = p.replace("\\\\", "\\").replace("/", os.sep)
            if os.path.exists(cleaned_path):
                library_paths.append(cleaned_path)
            else:
                if log_callback:
                    log_callback(f"Warning: Found VDF library path that does not exist: {cleaned_path}")
    except Exception as e:
        if log_callback:
            log_callback(f"Error parsing libraryfolders.vdf ({vdf_path}): {e}")
    return library_paths

def _parse_appmanifest_acf(acf_path, log_callback=None):
    install_dir = None
    try:
        with open(acf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'"installdir"\s*"(.*?)"', content)
        if match:
            install_dir = match.group(1)
    except Exception as e:
        if log_callback:
            log_callback(f"Error parsing appmanifest_730.acf ({acf_path}): {e}")
    return install_dir

def auto_detect_cs2_path(log_callback=None):
    if log_callback:
        log_callback("Attempting to auto-detect CS2 server executable...")
    steam_install_paths = _find_steam_installations()
    found_path = None

    if not steam_install_paths:
        if log_callback:
            log_callback("No common Steam installation paths found. Please ensure Steam is installed.")
        return None

    for steam_path in steam_install_paths:
        library_folders_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(library_folders_path):
            if log_callback:
                log_callback(f"Found libraryfolders.vdf at: {library_folders_path}")
            library_paths = _parse_library_folders_vdf(library_folders_path, log_callback)
            library_paths.insert(0, steam_path) # Add the main Steam path as a primary library

            for lib_path in library_paths:
                cleaned_lib_path = lib_path.strip('"')
                
                cs2_appmanifest_path = os.path.join(cleaned_lib_path, "steamapps", "appmanifest_730.acf")
                if os.path.exists(cs2_appmanifest_path):
                    if log_callback:
                        log_callback(f"Found appmanifest_730.acf at: {cs2_appmanifest_path}")
                    cs2_install_dir = _parse_appmanifest_acf(cs2_appmanifest_path, log_callback)
                    if cs2_install_dir:
                        potential_exe_path = os.path.join(
                            cleaned_lib_path,
                            "steamapps",
                            "common",
                            cs2_install_dir,
                            "game",
                            "bin",
                            "win64",
                            "cs2.exe"
                        )
                        if os.path.exists(potential_exe_path):
                            found_path = potential_exe_path
                            break # Found it, exit inner loop
            if found_path:
                break # Found it, exit outer loop
    return found_path


def detect_ip_address(log_callback=None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public IP to get the local IP used for outgoing connections
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        if log_callback:
            log_callback(f"Detected IP address: {ip_address}")
        return ip_address
    except Exception as e:
        if log_callback:
            log_callback(f"Error detecting IP address: {e}")
        return None