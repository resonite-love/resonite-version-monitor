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

def parse_manifests(app_info_output):
    """Parse manifest GIDs from app_info_print output (VDF format)."""
    manifests = {}
    
    # Find the depots section - look for "depots" followed by opening brace
    depots_start = app_info_output.find('"depots"')
    if depots_start == -1:
        return manifests
    
    # Find the corresponding closing brace for depots section
    brace_count = 0
    i = depots_start
    depots_end = -1
    inside_quotes = False
    
    while i < len(app_info_output):
        char = app_info_output[i]
        
        # Track if we're inside quotes
        if char == '"' and (i == 0 or app_info_output[i-1] != '\\'):
            inside_quotes = not inside_quotes
        
        # Only count braces outside of quotes
        if not inside_quotes:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and i > depots_start:
                    depots_end = i + 1
                    break
        i += 1
    
    if depots_end == -1:
        return manifests
    
    depots_content = app_info_output[depots_start:depots_end]
    
    # Look for depot entries with numeric IDs
    depot_pattern = r'"(\d+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    
    for depot_match in re.finditer(depot_pattern, depots_content):
        depot_id = depot_match.group(1)
        depot_content = depot_match.group(2)
        
        # Look for manifests section within this depot
        manifests_match = re.search(r'"manifests"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', depot_content)
        if manifests_match:
            manifests_content = manifests_match.group(1)
            
            depot_manifests = {}
            
            # Parse each branch's manifest
            branch_pattern = r'"([^"]+)"\s*\{([^{}]*)\}'
            for branch_match in re.finditer(branch_pattern, manifests_content):
                branch_name = branch_match.group(1)
                branch_content = branch_match.group(2)
                
                # Extract GID
                gid_match = re.search(r'"gid"\s*"(\d+)"', branch_content)
                if gid_match:
                    depot_manifests[branch_name] = gid_match.group(1)
            
            if depot_manifests:
                manifests[depot_id] = depot_manifests
    
    return manifests

def main():
    app_id = 2519830  # Resonite
    
    print(f"Fetching app info for {app_id}...")
    app_info = get_app_info(app_id)
    
    print("Parsing manifests...")
    print(app_info)
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