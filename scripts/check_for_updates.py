#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

def load_json(file_path):
    """Load JSON file if it exists."""
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def compare_manifests(current, previous):
    """Compare current and previous manifests to detect changes."""
    changes = []
    
    if not previous:
        return True, ["No previous data found - initial run"]
    
    current_manifests = current.get('manifests', {})
    previous_manifests = previous.get('manifests', {})
    
    # Check for new depots
    for depot_id in current_manifests:
        if depot_id not in previous_manifests:
            changes.append(f"New depot found: {depot_id}")
    
    # Check for removed depots
    for depot_id in previous_manifests:
        if depot_id not in current_manifests:
            changes.append(f"Depot removed: {depot_id}")
    
    # Check for manifest changes
    for depot_id, current_data in current_manifests.items():
        if depot_id in previous_manifests:
            previous_data = previous_manifests[depot_id]
            
            # Check public manifest
            if current_data.get('public') != previous_data.get('public'):
                changes.append(
                    f"Depot {depot_id} public manifest changed: "
                    f"{previous_data.get('public', 'none')} -> {current_data.get('public', 'none')}"
                )
            
            # Check beta manifest
            if current_data.get('beta') != previous_data.get('beta'):
                changes.append(
                    f"Depot {depot_id} beta manifest changed: "
                    f"{previous_data.get('beta', 'none')} -> {current_data.get('beta', 'none')}"
                )
    
    return len(changes) > 0, changes

def main():
    data_dir = Path(__file__).parent.parent / 'data'
    current_file = data_dir / 'current_manifests.json'
    previous_file = data_dir / 'previous_manifests.json'
    
    # Load current manifests
    current_data = load_json(current_file)
    if not current_data:
        print("Error: No current manifest data found")
        sys.exit(1)
    
    # Load previous manifests
    previous_data = load_json(previous_file)
    
    # Compare manifests
    has_changes, changes = compare_manifests(current_data, previous_data)
    
    if has_changes:
        print("Changes detected!")
        for change in changes:
            print(f"  - {change}")
        
        # Save current as previous for next run
        with open(previous_file, 'w') as f:
            json.dump(current_data, f, indent=2)
        
        # Set output for GitHub Actions
        print(f"::set-output name=has_changes::true")
        print(f"::set-output name=timestamp::{datetime.utcnow().isoformat()}")
        
        # Create a summary of changes for the commit message
        change_summary = "; ".join(changes[:3])  # First 3 changes
        if len(changes) > 3:
            change_summary += f" and {len(changes) - 3} more"
        print(f"::set-output name=change_summary::{change_summary}")
    else:
        print("No changes detected")
        print(f"::set-output name=has_changes::false")

if __name__ == '__main__':
    main()