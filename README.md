# Ski Tracks Recovery Generator

An unofficial Python tool for reconstructing lost **Ski Tracks** season statistics by generating synthetic `.skiz` activities that can be imported back into the Ski Tracks app.

> **Important:** This tool does not recover deleted GPS recordings. It creates replacement activities using the season totals you provide.

## Why this exists

This project started after Ski Tracks data was lost during a phone transfer.

Some season totals were still known — such as:

- number of ski days
- total distance
- total vertical
- maximum speed

—but the individual activities were gone.

By examining exported `.skiz` files and testing how Ski Tracks imports them, it was possible to create synthetic activities that Ski Tracks recognizes as real skiing activities.

This tool automates that process.

## What can be reconstructed?

You can configure each season with:

- **Number of ski days**
- **Total ski distance**
- **Total vertical**
- **Maximum speed**
- **Approximate start date**
- **Approximate end date**

The generator divides the requested distance and vertical across the requested number of days and creates an individual `.skiz` file for each activity.

For example:

```json
{
  "season": "2023-2024",
  "days": 58,
  "distance_km": 1049.1,
  "vertical_m": 222838,
  "max_speed_kmh": 87.9,
  "start_date": "2023-11-15",
  "end_date": "2024-04-15"
}
```

This generates **58 Ski Tracks activities** whose combined statistics target:

| Statistic | Value |
|---|---:|
| Ski days | 58 |
| Distance | 1049.1 km |
| Vertical | 222,838 m |
| Maximum speed | 87.9 km/h |

## What cannot be recovered?

Unless you still have the original recordings, this tool cannot reconstruct your actual:

- GPS routes
- ski resorts
- exact ski dates
- exact runs and lifts
- exact altitude profile
- exact speed profile
- pauses
- recording times

The generated GPS tracks are **synthetic**.

The purpose is to restore lost statistics and activity entries — not recreate historical GPS data that no longer exists.

## Requirements

You need:

- Python 3
- the files from this repository
- Ski Tracks on your phone

No additional Python packages are required.

## Download

You can either clone the repository with Git:

```bash
git clone https://github.com/Antistoffer/ski-tracks-recovery-generator.git
```

or use:

**Code → Download ZIP**

on GitHub.

Extract the ZIP before continuing.

## Files

The important files are:

```text
ski-tracks-recovery-generator/
├── README.md
├── example_config.json
├── generate_recovery.py
└── template.skiz
```

`generate_recovery.py` is the generator.

`example_config.json` contains your recovery settings.

`template.skiz` provides the synthetic `.skiz` structure used when generating replacement activities.

## Configuration

Open:

```text
example_config.json
```

The default configuration looks similar to:

```json
{
  "duration_minutes_per_day": 45,
  "seasons": [
    {
      "season": "2023-2024",
      "days": 58,
      "distance_km": 1049.1,
      "vertical_m": 222838,
      "max_speed_kmh": 87.9,
      "start_date": "2023-11-15",
      "end_date": "2024-04-15"
    }
  ]
}
```

Change the values to match the statistics you want to reconstruct.

### `season`

A name for the season:

```json
"season": "2023-2024"
```

### `days`

Number of activities to generate:

```json
"days": 58
```

### `distance_km`

Total distance for the season:

```json
"distance_km": 1049.1
```

### `vertical_m`

Total downhill vertical:

```json
"vertical_m": 222838
```

### `max_speed_kmh`

Maximum speed you want represented for the season:

```json
"max_speed_kmh": 87.9
```

### `start_date` and `end_date`

The generated activities are spread across this date range:

```json
"start_date": "2023-11-15",
"end_date": "2024-04-15"
```

These do not need to be your original dates if you no longer know them.

## Multiple seasons

You can reconstruct several seasons in one run:

```json
{
  "duration_minutes_per_day": 45,
  "seasons": [
    {
      "season": "2022-2023",
      "days": 17,
      "distance_km": 254.7,
      "vertical_m": 50000,
      "max_speed_kmh": 97.5,
      "start_date": "2022-11-15",
      "end_date": "2023-04-15"
    },
    {
      "season": "2023-2024",
      "days": 58,
      "distance_km": 1049.1,
      "vertical_m": 222838,
      "max_speed_kmh": 87.9,
      "start_date": "2023-11-15",
      "end_date": "2024-04-15"
    }
  ]
}
```

## Generate the files

Open PowerShell, Terminal, Command Prompt, or the VS Code terminal in the project folder.

On Windows:

```powershell
python generate_recovery.py
```

On some systems you may need:

```bash
python3 generate_recovery.py
```

When successful, you should see something similar to:

```text
DONE
--------------------------------
Created 58 .skiz files
Output folder: ...
--------------------------------
```

## Output

A new `output` directory will be created.

For example:

```text
output/
└── 2023-2024/
    ├── 001_2023-11-15_18.088km_3843m.skiz
    ├── 002_2023-11-18_18.088km_3843m.skiz
    ├── 003_2023-11-20_18.088km_3843m.skiz
    ├── ...
    └── README.txt
```

Each `.skiz` file represents one synthetic ski activity.

## Importing into Ski Tracks

Transfer the generated `.skiz` files to your phone.

On iPhone, one method is:

1. Save or send a `.skiz` file to the phone.
2. Open the file.
3. Choose **Open With** / **Share**.
4. Select **Ski Tracks**.
5. Allow Ski Tracks to import the activity.

The exact wording may vary depending on your iOS version.

## Test before importing everything

**Do not immediately import hundreds of generated files.**

First import only **2 or 3 activities**.

Verify that Ski Tracks displays the expected:

- date
- total distance
- ski distance
- ski descent distance
- vertical
- altitude
- speed
- map

If those look correct, continue with the rest of the recovery set.

Large sets can take a while to import.

## Back up your data

Once your reconstructed activities are successfully imported, make a backup.

If possible, keep copies in more than one location.

Also keep the generated `.skiz` files. They give you another way to restore the reconstructed activities if necessary.

## How it works

A `.skiz` file is an archive containing several files used by Ski Tracks, including data such as:

```text
Segment.csv
Events.xml
RelativeAltitudeSensor.csv
Log.txt
Track.xml
RawLocations.csv
Nodes.csv
```

The generator creates synthetic GPS and altitude data and writes matching activity metadata.

The generated route moves downhill so that Ski Tracks recognizes it as a skiing descent.

Each generated activity receives its own identifiers so that multiple activities can be imported.

## Synthetic routes

The routes created by this project are intentionally artificial.

They are not intended to look like real ski runs.

If your original GPS recordings are gone, there is no reliable way for this tool to know where you actually skied.

The synthetic GPS data exists only so that Ski Tracks can interpret the reconstructed activity.

## Privacy warning

**Do not publish one of your own real `.skiz` recordings as a template.**

A real recording may contain information such as:

- GPS coordinates
- timestamps
- device information
- activity metadata

The template included with this project is intended to avoid requiring users to share their own recordings publicly.

## Troubleshooting

### `python` is not recognized

Install Python 3 and make sure Python is available from your terminal.

You can check with:

```powershell
python --version
```

On macOS/Linux, try:

```bash
python3 --version
```

### `Could not find example_config.json`

Make sure you are running the command from the same folder containing:

```text
generate_recovery.py
example_config.json
template.skiz
```

### `Could not find template.skiz`

Make sure `template.skiz` has not been renamed or moved.

### The generated files import but the statistics look wrong

Stop importing additional files.

Try a single generated activity first and compare:

- distance
- vertical
- speed
- date

Ski Tracks behavior may differ between app versions.

If you report an issue, include your Ski Tracks version, operating system/device, configuration values, and what you expected versus what the app displayed.

**Do not upload a private `.skiz` recording containing personal GPS data unless you understand what information it contains.**

## Limitations

This project was created through reverse engineering and import testing.

The `.skiz` format is not treated here as an official public specification, and future Ski Tracks versions may behave differently.

The generator has primarily been tested for reconstructing downhill skiing statistics.

## Contributing

Bug reports and improvements are welcome.

If you discover that a particular Ski Tracks version behaves differently, please open a GitHub issue and describe:

- Ski Tracks version
- device/OS
- configuration used
- expected result
- actual result

Please avoid posting private GPS recordings publicly.

## Disclaimer

This is an unofficial community project.

It is **not affiliated with, endorsed by, or supported by Ski Tracks or Core Coders Ltd.**

Use it at your own risk.

Always keep backups before importing reconstructed data.