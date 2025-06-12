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
    """Parse manifest GIDs from app_info_print output."""
    manifests = {}
    
    # Find the depots section
    depots_match = re.search(r'"depots"\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', app_info_output)
    if not depots_match:
        return manifests
    
    depots_content = depots_match.group(0)
    
    # Find all depot entries with manifests
    depot_pattern = r'"(\d+)"\s*{[^}]*"manifests"\s*{([^}]*)}'
    
    for match in re.finditer(depot_pattern, depots_content):
        depot_id = match.group(1)
        manifest_content = match.group(2)
        
        # Extract public manifest GID
        public_match = re.search(r'"public"\s*"(\d+)"', manifest_content)
        if public_match:
            manifests[depot_id] = {
                'public': public_match.group(1)
            }
        
        # Extract beta manifest GID if present
        beta_match = re.search(r'"beta"\s*"(\d+)"', manifest_content)
        if beta_match and depot_id in manifests:
            manifests[depot_id]['beta'] = beta_match.group(1)
    
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