#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_version_entries(manifest_data, timestamp):
    """Create version entries from manifest data."""
    manifests = manifest_data.get('manifests', {})
    
    # Focus on depot 2519832 as requested
    depot_2519832 = manifests.get('2519832', {})
    
    if not depot_2519832:
        print("Warning: Depot 2519832 not found in manifest data")
        return None
    
    # Create entries for each branch
    entries = {}
    for branch_name, gid in depot_2519832.items():
        entries[branch_name] = {
            'manifestId': gid,
            'timestamp': timestamp,
            'gameVersion': None
        }
    
    return entries

def update_versions_json(manifest_data):
    """Update versions.json with new manifest data."""
    versions_file = Path(__file__).parent.parent / 'data' / 'versions.json'
    
    # Load existing versions or create new
    if versions_file.exists():
        versions_data = load_json(versions_file)
    else:
        # Initialize with empty arrays for each branch
        versions_data = {
            'public': [],
            'prerelease': [],
            'release': [],
            'headless': []
        }
    
    # Create new version entries
    timestamp = datetime.utcnow().isoformat() + 'Z'
    new_entries = create_version_entries(manifest_data, timestamp)
    
    if new_entries:
        updated = False
        
        # Process each branch
        for branch_name, new_entry in new_entries.items():
            # Initialize branch if it doesn't exist
            if branch_name not in versions_data:
                versions_data[branch_name] = []
            
            # Check if this GID already exists for this branch
            existing_gids = [v.get('manifestId') for v in versions_data[branch_name]]
            
            if new_entry['manifestId'] not in existing_gids:
                versions_data[branch_name].append(new_entry)
                updated = True
                print(f"Added new entry for {branch_name}: {new_entry['manifestId']}")
            else:
                print(f"GID {new_entry['manifestId']} already exists for branch {branch_name}")
        
        if updated:
            # Save updated versions
            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
            
            print("Updated versions.json")
            return True
        else:
            print("No new changes to record")
    
    return False

def main():
    current_file = Path(__file__).parent.parent / 'data' / 'current_manifests.json'
    
    if not current_file.exists():
        print("Error: current_manifests.json not found")
        sys.exit(1)
    
    manifest_data = load_json(current_file)
    
    if update_versions_json(manifest_data):
        print("Successfully updated versions.json")
    else:
        print("No update needed for versions.json")

if __name__ == '__main__':
    main()