import os
import re
import socket
import struct # For reading binary file headers

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
        with open(vdf_path, 'r') as f:
            content = f.read()
            # Regex to find all "path" values within the VDF file
            paths_found = re.findall(r'"path"\s+"(.*?)"', content)
            for path in paths_found:
                # Normalize paths (replace double backslashes with single ones, then convert to os-specific)
                normalized_path = path.replace('\\\\', '\\')
                if os.path.exists(normalized_path):
                    library_paths.append(normalized_path)
                    if log_callback:
                        log_callback(f"Found Steam library: {normalized_path}")
    except FileNotFoundError:
        if log_callback:
            log_callback(f"libraryfolders.vdf not found at {vdf_path}")
    except Exception as e:
        if log_callback:
            log_callback(f"Error parsing libraryfolders.vdf at {vdf_path}: {e}")
    return library_paths

def _parse_appmanifest_acf(acf_path, log_callback=None):
    """
    Parses an appmanifest_730.acf file to find the 'installdir' for CS2 (AppId 730).
    """
    try:
        with open(acf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Use regex to find the "installdir" key and its value
            match = re.search(r'"installdir"\s+"(.*?)"', content)
            if match:
                install_dir = match.group(1)
                if log_callback:
                    log_callback(f"Found installdir '{install_dir}' in {acf_path}")
                return install_dir
            else:
                if log_callback:
                    log_callback(f"installdir not found in {acf_path}")
                return None
    except FileNotFoundError:
        if log_callback:
            log_callback(f"appmanifest_730.acf not found at {acf_path}")
        return None
    except Exception as e:
        if log_callback:
            log_callback(f"Error parsing appmanifest_730.acf at {acf_path}: {e}")
        return None

def auto_detect_cs2_path(log_callback=None):
    found_path = None
    steam_paths = _find_steam_installations()
    if not steam_paths and log_callback:
        log_callback("No Steam installations found.")
        return None

    for steam_path in steam_paths:
        if log_callback:
            log_callback(f"Checking Steam installation at: {steam_path}")
        
        # Check default steamapps location
        steamapps_path = os.path.join(steam_path, "steamapps")
        if not os.path.exists(steamapps_path):
            print("t")
            continue

        vdf_path = os.path.join(steamapps_path, "libraryfolders.vdf")
        
        # Get additional library folders
        library_folders = [steamapps_path]
        if os.path.exists(vdf_path):
            library_folders.extend(_parse_library_folders_vdf(vdf_path, log_callback))
        
        for lib_path in set(library_folders): # Use set to avoid duplicates
            cleaned_lib_path = lib_path.replace('\\\\', '\\') # Normalize path
            cs2_appmanifest_path = os.path.join(cleaned_lib_path, "steamapps", "appmanifest_730.acf")

            if not os.path.exists(cs2_appmanifest_path):
                continue

            if log_callback:
                log_callback(f"Found appmanifest_730.acf at: {cs2_appmanifest_path}")

            cs2_install_dir = _parse_appmanifest_acf(cs2_appmanifest_path, log_callback)
            if not cs2_install_dir:
                continue

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
        
    log_callback(found_path)
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
        return "0.0.0.0" # Fallback to 0.0.0.0 (listens on all available IPs)

def validate_vpk_integrity(vpk_path: str, log_callback=None) -> bool:
    """
    Performs a basic integrity check on a VPK file by reading its header.
    This does not fully validate the VPK, but checks if it's a recognizable VPK format.
    """
    if not os.path.exists(vpk_path):
        if log_callback:
            log_callback(f"VPK file not found: {vpk_path}")
        return False
    
    try:
        with open(vpk_path, 'rb') as f:
            # VPK header consists of signature (0x55AA1234), version, and header size
            signature = struct.unpack('<I', f.read(4))[0] # Little-endian unsigned int
            if signature != 0x55AA1234:
                if log_callback:
                    log_callback(f"VPK validation failed: Invalid signature for {vpk_path}")
                return False
            
            # Read version and header size (for version 2)
            version, header_size = struct.unpack('<II', f.read(8)) # Version, Header Size
            if version < 2: # Older VPK versions might not be compatible
                 if log_callback:
                    log_callback(f"VPK validation failed: Unsupported VPK version ({version}). Expected 2 or higher: {vpk_path}")
                 # return False # Uncomment to strictly enforce version 2+
            
            if log_callback:
                log_callback(f"VPK validation: Passed basic header check for {vpk_path}")
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"Error reading VPK file {vpk_path}: {e}")
        return False

def get_map_name_from_vpk(vpk_path: str, log_callback=None) -> str:
    """
    Attempts to derive a map name from the VPK filename.
    A more accurate method would involve parsing the VPK's content, which is beyond
    the scope of simple file operations.
    """
    if not vpk_path:
        return ""
    
    base_name = os.path.basename(vpk_path)
    map_name = os.path.splitext(base_name)[0] # Remove .vpk extension
    
    # Simple heuristic: if the VPK name starts with 'ws_', remove it (common for workshop downloads)
    if map_name.lower().startswith("ws_"):
        map_name = map_name[3:]
        if log_callback:
            log_callback(f"Stripped 'ws_' prefix from VPK name. Derived map name: {map_name}")
    
    return map_name