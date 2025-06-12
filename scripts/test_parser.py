#!/usr/bin/env python3
import sys
from pathlib import Path
from fetch_app_info import parse_manifests

def test_parser():
    """Test the VDF parser with the sample file."""
    sample_file = Path(__file__).parent.parent / 'sample_appid_responce'
    
    if not sample_file.exists():
        print(f"Sample file not found: {sample_file}")
        return
    
    with open(sample_file, 'r') as f:
        sample_data = f.read()
    
    print("Testing VDF parser...")
    manifests = parse_manifests(sample_data)
    
    print(f"\nFound {len(manifests)} depots with manifests:")
    for depot_id, branches in manifests.items():
        print(f"\nDepot {depot_id}:")
        for branch, gid in branches.items():
            print(f"  {branch}: {gid}")
    
    # Check if depot 2519832 was found
    if '2519832' in manifests:
        print(f"\n✓ Successfully found depot 2519832 with branches: {list(manifests['2519832'].keys())}")
    else:
        print("\n✗ Failed to find depot 2519832")

if __name__ == '__main__':
    test_parser()