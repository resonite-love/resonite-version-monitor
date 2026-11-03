#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(file_path, data):
    """Save JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def download_build_version(app_id, depot_id, manifest_id, branch):
    """Download Build.version file using DepotDownloader."""
    depot_downloader = './DepotDownloader/DepotDownloader'
    
    # Create temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create filelist file
        filelist_path = Path(temp_dir) / 'filelist.txt'
        with open(filelist_path, 'w') as f:
            f.write('Build.version\n')
        
        cmd = [
            depot_downloader,
            '-app', str(app_id),
            '-depot', str(depot_id),
            '-manifest', manifest_id,
            '-username', os.environ.get('STEAM_USERNAME', ''),
            '-password', os.environ.get('STEAM_PASSWORD', ''),
            '-remember-password',
            '-dir', temp_dir,
            '-filelist', str(filelist_path)
        ]
        
        # Preserve Steam's exact branch name, including public and release.
        cmd.extend(['-branch', branch])

        # Keep the existing headless beta-key configuration.
        if branch == 'headless':
            beta_key = os.environ.get('STEAM_BETA_KEY', '')
            if beta_key:
                cmd.extend(['-branchpassword', beta_key])
        
        print(f"Downloading Build.version for {branch} (manifest: {manifest_id})...")
        
        try:
            # Run DepotDownloader
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error downloading: {result.stderr}")
                return None
            
            # Read the Build.version file
            build_version_path = Path(temp_dir) / 'Build.version'
            if build_version_path.exists():
                with open(build_version_path, 'r') as f:
                    version = f.read().strip()
                print(f"Found version: {version}")
                return version
            else:
                print("Build.version file not found in download")
                return None
                
        except Exception as e:
            print(f"Exception during download: {e}")
            return None

def update_versions_with_game_version(branch='all', versions_file=None):
    """Update versions.json with game versions."""
    versions_file = Path(versions_file) if versions_file is not None else Path(__file__).parent.parent / 'data' / 'versions.json'
    
    if not versions_file.exists():
        print("versions.json not found")
        return False
    
    versions_data = load_json(versions_file)
    if branch != 'all' and branch not in versions_data:
        raise ValueError(f"Unknown branch '{branch}'. Available branches: {', '.join(versions_data)}")
    branches = list(versions_data) if branch == 'all' else [branch]
    app_id = 2519830
    depot_id = 2519832
    updated = False
    max_failures = 3  # Skip the rest of a branch after consecutive download failures.
    
    # Process each branch
    for branch_name in branches:
        failed_count = 0
        
        # Process entries that don't have gameVersion
        for entry in versions_data[branch_name]:
            if entry.get('gameVersion') is None:
                manifest_id = entry.get('manifestId')
                if manifest_id:
                    print(f"\nProcessing {branch_name} manifest: {manifest_id}")
                    
                    # Download and extract version
                    game_version = download_build_version(app_id, depot_id, manifest_id, branch_name)
                    
                    if game_version:
                        entry['gameVersion'] = game_version
                        updated = True
                        failed_count = 0  # Reset failure counter on success
                        print(f"Updated {branch_name} entry with version: {game_version}")
                        
                        # Save progress periodically (every successful update)
                        save_json(versions_file, versions_data)
                    else:
                        print(f"Failed to get version for {branch_name} manifest: {manifest_id}")
                        failed_count += 1
                        
                        # An inaccessible branch must not block other branches.
                        if failed_count >= max_failures:
                            print(f"\nSkipping remaining {branch_name} entries after {max_failures} consecutive failures")
                            break
    
    if updated:
        save_json(versions_file, versions_data)
        print("\nSaved successfully retrieved game versions")
        return True
    else:
        print("\nNo game versions updated")
        return False

def main(argv=None):
    parser = argparse.ArgumentParser(description='Fill missing game versions for recorded Steam branches.')
    parser.add_argument('--branch', default=os.environ.get('VERSION_BRANCH') or 'all',
                        help='Steam branch name from versions.json, or all (default: VERSION_BRANCH or all)')
    args = parser.parse_args(argv)
    # Check if Steam credentials are provided
    if not os.environ.get('STEAM_USERNAME') or not os.environ.get('STEAM_PASSWORD'):
        print("Error: STEAM_USERNAME and STEAM_PASSWORD must be set")
        return
    
    try:
        update_versions_with_game_version(branch=args.branch)
    except ValueError as error:
        parser.error(str(error))

if __name__ == '__main__':
    main()
