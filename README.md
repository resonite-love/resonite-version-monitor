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
- `data/versions.json` - Historical record of depot 2519832 GID changes

## Setup

1. Fork/clone this repository
2. Enable GitHub Actions in your repository
3. The workflow will run automatically on schedule

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
      "depotid": "8412389452125882142",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ],
  "prerelease": [
    {
      "depotid": "4281492182895112523",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ],
  "release": [
    {
      "depotid": "8412389452125882142",
      "timestamp": "2025-01-13T12:00:00Z",
      "gameVersion": null
    }
  ]
}
```

Each branch tracks its complete history separately, with new entries added when the depot GID changes.