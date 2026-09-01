# Ski Tracks Recovery Generator

Unofficial recovery/reconstruction utility for creating synthetic `.skiz` activities that can restore lost Ski Tracks season totals.

## Important

This tool does **not** recover deleted GPS recordings. It creates synthetic downhill skiing activities from totals you provide.

You can configure:
- number of ski days
- total distance
- total vertical
- season maximum speed
- date range

The generated GPS routes are synthetic.

This project is not affiliated with Ski Tracks or Core Coders Ltd.

## Requirements

- Python 3
- `template.skiz` from this repository

No extra Python packages are required.

## Quick start

1. Download or clone this repository.
2. Edit `example_config.json`.
3. Open a terminal in the repository folder.
4. Run:

```powershell
python generate_recovery.py
```

5. Generated activities appear in `output/`.

## Recommended import process

Import 2-3 generated activities first and verify date, distance, descent distance, vertical, map, and speed before importing a large recovery set.

## Privacy

Do not publish your own real `.skiz` recording as a template. Real recordings may contain GPS coordinates, timestamps, and device metadata.

## Disclaimer

Use at your own risk and keep backups before importing reconstructed activities.
