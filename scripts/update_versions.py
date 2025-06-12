#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_version_entry(manifest_data, timestamp):
    """Create a version entry from manifest data."""
    manifests = manifest_data.get('manifests', {})
    
    # Focus on depot 2519832 as requested
    depot_2519832 = manifests.get('2519832', {})
    
    if not depot_2519832:
        print("Warning: Depot 2519832 not found in manifest data")
        return None
    
    # Extract GIDs for all branches in depot 2519832
    entry = {
        'timestamp': timestamp,
        'depot_2519832': depot_2519832,  # Store all branches
        'all_depots': manifests  # Store all depot info for reference
    }
    
    # Add specific fields for easy access
    if 'public' in depot_2519832:
        entry['depot_2519832_public_gid'] = depot_2519832['public']
    if 'prerelease' in depot_2519832:
        entry['depot_2519832_prerelease_gid'] = depot_2519832['prerelease']
    if 'release' in depot_2519832:
        entry['depot_2519832_release_gid'] = depot_2519832['release']
    
    return entry

def update_versions_json(manifest_data):
    """Update versions.json with new manifest data."""
    versions_file = Path(__file__).parent.parent / 'data' / 'versions.json'
    
    # Load existing versions or create new
    if versions_file.exists():
        versions_data = load_json(versions_file)
    else:
        versions_data = {
            'app_id': 2519830,
            'tracked_depot': '2519832',
            'versions': []
        }
    
    # Create new version entry
    timestamp = datetime.utcnow().isoformat() + 'Z'
    new_entry = create_version_entry(manifest_data, timestamp)
    
    if new_entry:
        # Check if any GID has changed (avoid duplicates)
        should_update = False
        
        # Check if we have any existing versions
        if versions_data.get('versions'):
            last_entry = versions_data['versions'][-1]
            
            # Compare all branches in depot 2519832
            last_depot = last_entry.get('depot_2519832', {})
            current_depot = new_entry.get('depot_2519832', {})
            
            if last_depot != current_depot:
                should_update = True
        else:
            # No existing versions, always add the first one
            should_update = True
        
        if should_update:
            versions_data['versions'].append(new_entry)
            
            # Keep only last 100 versions
            versions_data['versions'] = versions_data['versions'][-100:]
            
            # Save updated versions
            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
            
            print(f"Updated versions.json with depot 2519832 changes")
            return True
        else:
            print(f"No changes detected in depot 2519832")
    
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