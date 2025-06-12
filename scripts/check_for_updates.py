#!/usr/bin/env python3
import json
import sys
import os
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
    
    # Check for manifest changes in each depot
    for depot_id, current_branches in current_manifests.items():
        if depot_id in previous_manifests:
            previous_branches = previous_manifests[depot_id]
            
            # Check each branch (public, prerelease, release, etc.)
            for branch_name, current_gid in current_branches.items():
                previous_gid = previous_branches.get(branch_name)
                
                if previous_gid != current_gid:
                    changes.append(
                        f"Depot {depot_id} {branch_name} manifest changed: "
                        f"{previous_gid or 'none'} -> {current_gid}"
                    )
            
            # Check for new branches
            for branch_name in current_branches:
                if branch_name not in previous_branches:
                    changes.append(f"New branch '{branch_name}' added to depot {depot_id}")
            
            # Check for removed branches
            for branch_name in previous_branches:
                if branch_name not in current_branches:
                    changes.append(f"Branch '{branch_name}' removed from depot {depot_id}")
    
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
        
        # Set output for GitHub Actions (new format)
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"has_changes=true\n")
            f.write(f"timestamp={datetime.utcnow().isoformat()}\n")
            
            # Create a summary of changes for the commit message
            change_summary = "; ".join(changes[:3])  # First 3 changes
            if len(changes) > 3:
                change_summary += f" and {len(changes) - 3} more"
            f.write(f"change_summary={change_summary}\n")
    else:
        print("No changes detected")
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"has_changes=false\n")

if __name__ == '__main__':
    main()