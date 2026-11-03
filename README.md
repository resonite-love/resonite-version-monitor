# Resonite Version Monitor

This project monitors Resonite (App ID: 2519830) for updates by checking Steam manifest changes, specifically focusing on depot 2519832.

## How it works

1. **GitHub Actions** runs every five minutes (or manually triggered)
2. **SteamCMD** fetches current app info using `app_info_print 2519830`
3. **Python scripts** parse the manifest data and detect changes
4. If depot 2519832's GID changes, `versions.json` is updated for every discovered branch
5. Changes are automatically committed and pushed

## Files

- `scripts/fetch_app_info.py` - Downloads and runs SteamCMD to get app info
- `scripts/check_for_updates.py` - Compares current vs previous manifests
- `scripts/update_versions.py` - Updates versions.json with new GIDs
- `scripts/update_game_versions.py` - Downloads Build.version files and updates gameVersion
- `data/versions.json` - Historical record of depot 2519832 GID changes

## Workflows

1. **Check Resonite Updates** - Monitors manifest changes and updates versions.json
2. **Update Game Version** - Downloads Build.version files and updates gameVersion fields

## Setup

1. Fork/clone this repository
2. Enable GitHub Actions in your repository
3. Add Steam credentials as GitHub Secrets:
   - `STEAM_USERNAME`: Your Steam username
   - `STEAM_PASSWORD`: Your Steam password
   - `STEAM_BETA_KEY`: Beta key for accessing headless branch
   - Username/password are required for downloading Build.version files. `STEAM_BETA_KEY` is only passed for the `headless` branch; other protected branches require access through the Steam account.
4. The workflow will run automatically on schedule

## Manual Run

To manually trigger the check:
1. Go to Actions tab
2. Select "Check Resonite Updates"
3. Click "Run workflow"

To fill missing game versions for a particular branch, run **Update Game Version**
and enter its exact Steam name (for example `alpha-prime` or `pre-splittening`).
The default `all` processes every branch recorded in `data/versions.json`.
New branches are picked up automatically after **Check Resonite Updates** records
their depot manifests; no branch allowlist needs to be edited.

The same selection is available locally, with DepotDownloader installed at
`./DepotDownloader/DepotDownloader` and the Steam credentials set in the environment:

```sh
python scripts/update_game_versions.py --branch alpha-prime
python scripts/update_game_versions.py --branch all
```

`VERSION_BRANCH` can also set the default branch; `--branch` takes precedence.
An unknown branch name is reported as an error. Existing game versions are left
unchanged. After three consecutive download failures within a branch, its remaining
entries are skipped for that run and processing continues with the other branches.
Unresolved entries retain `gameVersion: null` and can be retried on the next run.

## Data Format

`versions.json` contains:
```json
{
  "public": [
    {
      "manifestId": "8412389452125882142",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ],
  "prerelease": [
    {
      "manifestId": "4281492182895112523",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ],
  "release": [
    {
      "manifestId": "8412389452125882142",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ],
  "headless": [
    {
      "manifestId": "1234567890123456789",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ]
}
```

Branch keys are dynamic: `alpha-prime`, `pre-splittening`, and any future branches
with readable manifests for depot 2519832 use the same format. `public` and `release`
remain separate even when their manifest IDs match. Each branch tracks its history
separately, starting when it is first detected, with new entries added when a new
depot GID is observed. History is retained when a branch disappears from Steam.
Encrypted manifests without a readable GID cannot be recorded by the monitor.

## Tests

Run the offline regression tests without Steam credentials or downloads:

```sh
python -m unittest discover -s scripts -p "test_*.py" -v
```
