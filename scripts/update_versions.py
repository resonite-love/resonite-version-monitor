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
    
    # Get the public manifest GID for depot 2519832
    gid = depot_2519832.get('public')
    
    if not gid:
        print("Warning: No public manifest GID found for depot 2519832")
        return None
    
    return {
        'timestamp': timestamp,
        'depot_2519832_gid': gid,
        'all_depots': manifests  # Store all depot info for reference
    }

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
        # Check if this GID already exists (avoid duplicates)
        existing_gids = [v.get('depot_2519832_gid') for v in versions_data.get('versions', [])]
        
        if new_entry['depot_2519832_gid'] not in existing_gids:
            versions_data['versions'].append(new_entry)
            
            # Keep only last 100 versions
            versions_data['versions'] = versions_data['versions'][-100:]
            
            # Save updated versions
            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
            
            print(f"Updated versions.json with new GID: {new_entry['depot_2519832_gid']}")
            return True
        else:
            print(f"GID {new_entry['depot_2519832_gid']} already exists in versions.json")
    
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