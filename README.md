# Resonite Version Monitor

This project monitors Resonite (App ID: 2519830) for updates by checking Steam manifest changes, specifically focusing on depot 2519832.

## How it works

1. **GitHub Actions** runs every hour (or manually triggered)
2. **SteamCMD** fetches current app info using `app_info_print 2519830`
3. **Python scripts** parse the manifest data and detect changes
4. If depot 2519832's GID changes, `versions.json` is updated
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
   - These are required for downloading Build.version files and accessing beta branches
4. The workflow will run automatically on schedule

## Manual Run

To manually trigger the check:
1. Go to Actions tab
2. Select "Check Resonite Updates"
3. Click "Run workflow"

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

Each branch tracks its complete history separately, with new entries added when the depot GID changes.