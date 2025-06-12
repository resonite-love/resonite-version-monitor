#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import re
from pathlib import Path

def setup_steamcmd():
    """Download and setup SteamCMD if not already present."""
    steamcmd_dir = Path.home() / '.steam' / 'steamcmd'
    steamcmd_dir.mkdir(parents=True, exist_ok=True)
    
    steamcmd_path = steamcmd_dir / 'steamcmd.sh'
    
    if not steamcmd_path.exists():
        print("Downloading SteamCMD...")
        subprocess.run([
            'wget', '-q', '-O', str(steamcmd_dir / 'steamcmd_linux.tar.gz'),
            'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz'
        ], check=True)
        
        subprocess.run([
            'tar', '-xzf', str(steamcmd_dir / 'steamcmd_linux.tar.gz'),
            '-C', str(steamcmd_dir)
        ], check=True)
        
        (steamcmd_dir / 'steamcmd_linux.tar.gz').unlink()
    
    return str(steamcmd_path)

def get_app_info(app_id):
    """Fetch app info from Steam using SteamCMD."""
    steamcmd = setup_steamcmd()
    
    # Run SteamCMD with app_info_print command
    cmd = [
        steamcmd,
        '+login', 'anonymous',
        '+app_info_print', str(app_id),
        '+quit'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running SteamCMD: {result.stderr}")
        sys.exit(1)
    
    return result.stdout

def parse_vdf_section(text, start_pos=0):
    """Parse a VDF section and return its content as a dictionary."""
    result = {}
    i = start_pos
    
    while i < len(text):
        # Skip whitespace
        while i < len(text) and text[i] in ' \t\n\r':
            i += 1
        
        if i >= len(text):
            break
            
        # Check for closing brace
        if text[i] == '}':
            return result, i + 1
        
        # Parse key
        if text[i] == '"':
            i += 1
            key_start = i
            while i < len(text) and text[i] != '"':
                if text[i] == '\\' and i + 1 < len(text):
                    i += 2
                else:
                    i += 1
            key = text[key_start:i]
            i += 1
            
            # Skip whitespace between key and value
            while i < len(text) and text[i] in ' \t\n\r':
                i += 1
            
            # Parse value
            if i < len(text):
                if text[i] == '"':
                    # String value
                    i += 1
                    value_start = i
                    while i < len(text) and text[i] != '"':
                        if text[i] == '\\' and i + 1 < len(text):
                            i += 2
                        else:
                            i += 1
                    value = text[value_start:i]
                    i += 1
                    result[key] = value
                elif text[i] == '{':
                    # Nested section
                    i += 1
                    value, new_i = parse_vdf_section(text, i)
                    i = new_i
                    result[key] = value
        else:
            i += 1
    
    return result, i

def parse_manifests(app_info_output):
    """Parse manifest GIDs from app_info_print output (VDF format)."""
    manifests = {}
    
    # Parse the entire VDF structure
    try:
        # Skip any leading output before the actual data
        data_start = app_info_output.find('{')
        if data_start == -1:
            print("Could not find start of VDF data")
            return manifests
            
        vdf_data, _ = parse_vdf_section(app_info_output, data_start + 1)
        
        # Navigate to depots section
        depots = vdf_data.get('depots', {})
        
        # Look for depot entries with manifests
        for depot_id, depot_data in depots.items():
            # Skip non-numeric depot IDs (like "branches", "baselanguages")
            if not depot_id.isdigit():
                continue
                
            if isinstance(depot_data, dict) and 'manifests' in depot_data:
                depot_manifests = {}
                manifests_data = depot_data['manifests']
                
                if isinstance(manifests_data, dict):
                    for branch_name, branch_data in manifests_data.items():
                        if isinstance(branch_data, dict) and 'gid' in branch_data:
                            depot_manifests[branch_name] = branch_data['gid']
                
                if depot_manifests:
                    manifests[depot_id] = depot_manifests
    
    except Exception as e:
        print(f"Error parsing VDF: {e}")
        import traceback
        traceback.print_exc()
    
    return manifests

def main():
    app_id = 2519830  # Resonite
    
    print(f"Fetching app info for {app_id}...")
    app_info = get_app_info(app_id)
    
    print("Parsing manifests...")
    manifests = parse_manifests(app_info)
    
    # Output as JSON
    output = {
        'app_id': app_id,
        'manifests': manifests
    }
    
    print(json.dumps(output, indent=2))
    
    # Save to file
    output_path = Path(__file__).parent.parent / 'data' / 'current_manifests.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    main()