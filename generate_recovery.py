import csv
import io
import json
import shutil
import uuid
import zipfile
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

CONFIG_FILE = Path("example_config.json")
TEMPLATE_FILE = Path("template.skiz")
OUTPUT_DIR = Path("output")

def make_csv(rows):
    s = io.StringIO()
    csv.writer(s, lineterminator="\\n").writerows(rows)
    return s.getvalue().encode("utf-8")

def iso_z(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def split_integer_total(total, count):
    total = int(round(total))
    base = total // count
    rem = total - base * count
    return [base + (1 if i < rem else 0) for i in range(count)]

def spread_dates(start_date, end_date, count):
    if count == 1:
        return [start_date]
    span = (end_date - start_date).days
    result, used = [], set()
    for i in range(count):
        d = start_date + timedelta(days=round(span * i / (count - 1)))
        while d in used:
            d += timedelta(days=1)
        used.add(d)
        result.append(d)
    return result

def build_activity(template_path, output_path, activity_date, day_number, season_name,
                   distance_m, vertical_m, max_speed_kmh, duration_minutes):
    start = datetime(activity_date.year, activity_date.month, activity_date.day,
                     9, 30, 0, tzinfo=timezone.utc)
    duration_s = float(duration_minutes) * 60.0
    finish = start + timedelta(seconds=duration_s)
    speed_ms = max_speed_kmh / 3.6
    points_n = 121
    start_lat, start_lon = 55.644, 12.5938
    finish_alt = 1000.0
    start_alt = finish_alt + vertical_m

    points = []
    for i in range(points_n):
        f = i / (points_n - 1)
        t = start + timedelta(seconds=duration_s * f)
        lat = start_lat + distance_m * f / 111_320.0
        alt = start_alt - vertical_m * f
        points.append((t.timestamp(), lat, start_lon, alt))

    nodes = make_csv([
        [f"{ts:.3f}", f"{lat:.9f}", f"{lon:.9f}", f"{speed_ms:.6f}",
         "0.00", "0.00", "5.00", f"{alt:.3f}"]
        for ts, lat, lon, alt in points
    ])

    raw = make_csv([
        [f"{ts:.3f}", f"{lat:.9f}", f"{lon:.9f}", f"{speed_ms:.6f}",
         "0.00", "0.00", "5.00", f"{alt:.3f}", f"{ts+0.030:.3f}"]
        for ts, lat, lon, alt in points
    ])

    rel_alt = make_csv([[f"{ts:.3f}", f"{alt:.3f}"] for ts, _, _, alt in points])

    start_iso, finish_iso = iso_z(start), iso_z(finish)
    events = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Created using CCXML v1.1.0 encoder library, © Core Coders Ltd. -->
<events>
        <event start="{start_iso}" end="{start_iso}" type="start"/>
        <event start="{finish_iso}" end="{finish_iso}" type="stop"/>
</events>
""".encode("utf-8")

    sid = str(uuid.uuid4()).upper()
    pid = uuid.uuid4().hex[:10]

    track = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Created using CCXML v1.1.0 encoder library, © Core Coders Ltd. -->
<track
        version="1.0"
        name="Recovered Day {day_number} - {season_name}"
        activity="skiing"
        start="{start.isoformat()}"
        finish="{finish.isoformat()}"
        tz="+00:00"
        duration="{duration_s:.3f}"
        platform="iPhone17,3/ios-26.5.2/SkiTracks-3.10.3.10.1"
        syncIdentifier="{sid}"
        syncVersion="1"
        parseObjectId="{pid}">
        <extensions>
                <location>
                        <lat>{start_lat:.14f}</lat>
                        <lon>{start_lon:.14f}</lon>
                </location>
        </extensions>
        <metrics>
                <maxspeed>{speed_ms:.6f}</maxspeed>
                <maxdescentspeed>{speed_ms:.6f}</maxdescentspeed>
                <maxascentspeed>0.00</maxascentspeed>
                <maxdescentsteepness>10.0</maxdescentsteepness>
                <maxascentsteepness>0.0</maxascentsteepness>
                <totalascent>0.0</totalascent>
                <totaldescent>{vertical_m:.3f}</totaldescent>
                <maxaltitude>{start_alt:.3f}</maxaltitude>
                <minaltitude>{finish_alt:.3f}</minaltitude>
                <distance>{distance_m:.3f}</distance>
                <descentdistance>{distance_m:.3f}</descentdistance>
                <ascentdistance>0.0</ascentdistance>
                <averagespeed>{speed_ms:.6f}</averagespeed>
                <averagedescentspeed>{speed_ms:.6f}</averagedescentspeed>
                <averageascentspeed>0.0</averageascentspeed>
                <movingaveragespeed>{speed_ms:.6f}</movingaveragespeed>
                <duration>{duration_s:.3f}</duration>
                <startaltitude>{start_alt:.3f}</startaltitude>
                <finishaltitude>{finish_alt:.3f}</finishaltitude>
                <ascents>0</ascents>
                <descents>1</descents>
        </metrics>
</track>
""".encode("utf-8")

    segment = make_csv([
        ["1"],
        [f"{points[0][0]:.6f}", f"{points[-1][0]:.6f}", "8", "0", "1",
         "Ski Run 1", "", "ski_run", "", "", "", f"{duration_s:.3f}",
         f"{speed_ms:.6f}", f"{distance_m:.6f}", f"{-vertical_m:.6f}",
         f"{speed_ms:.6f}", "10.000000", "10.000000",
         f"{start_alt:.6f}", f"{finish_alt:.6f}",
         f"{-vertical_m:.6f}", f"{distance_m:.6f}"]
    ])

    log = f"""{start.isoformat()} Debug Recording State Changing from Ready to Active
{start.isoformat()} Info kCLAuthorizationStatusAuthorizedAlways
{start.isoformat()} Info CCIOSLocationGenerator: Has GPS fix after 2 locations
{finish.isoformat()} Debug Recording State Changing from Active to Paused
""".encode("utf-8")

    repl = {
        "Segment.csv": segment,
        "Events.xml": events,
        "RelativeAltitudeSensor.csv": rel_alt,
        "Log.txt": log,
        "Track.xml": track,
        "RawLocations.csv": raw,
        "Nodes.csv": nodes,
    }

    with zipfile.ZipFile(template_path, "r") as zin, zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            name = Path(info.filename).name
            zout.writestr(info, repl.get(name, zin.read(info.filename)))

def main():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("Could not find example_config.json")
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError("Could not find template.skiz")

    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    seasons = config.get("seasons", [])
    if not seasons:
        raise ValueError("No seasons found in config.")

    duration = float(config.get("duration_minutes_per_day", 45))

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    total_files = 0

    for s in seasons:
        season_name = str(s["season"])
        days = int(s["days"])
        distance_total_m = int(round(float(s["distance_km"]) * 1000))
        vertical_total_m = int(round(float(s["vertical_m"])))
        max_speed = float(s["max_speed_kmh"])
        start_date = date.fromisoformat(s["start_date"])
        end_date = date.fromisoformat(s["end_date"])

        if days < 1 or distance_total_m <= 0 or vertical_total_m <= 0 or max_speed <= 0:
            raise ValueError(f"Invalid values in season {season_name}")

        dates = spread_dates(start_date, end_date, days)
        distances = split_integer_total(distance_total_m, days)
        verticals = split_integer_total(vertical_total_m, days)

        season_dir = OUTPUT_DIR / season_name
        season_dir.mkdir()

        for i in range(days):
            day_speed = max_speed if i == 0 else max_speed * 0.75
            filename = f"{i+1:03d}_{dates[i].isoformat()}_{distances[i]/1000:.3f}km_{verticals[i]}m.skiz"
            build_activity(
                TEMPLATE_FILE, season_dir / filename, dates[i], i+1, season_name,
                distances[i], verticals[i], day_speed, duration
            )
            total_files += 1

        (season_dir / "README.txt").write_text(
            f"Season: {season_name}\nActivities: {days}\n"
            f"Target distance: {distance_total_m/1000:.3f} km\n"
            f"Target vertical: {vertical_total_m} m\n"
            f"Target maximum speed: {max_speed:.1f} km/h\n"
            "These are synthetic reconstruction files, not recovered original GPS tracks.\n",
            encoding="utf-8"
        )

    print()
    print("DONE")
    print("--------------------------------")
    print(f"Created {total_files} .skiz files")
    print(f"Output folder: {OUTPUT_DIR.resolve()}")
    print("--------------------------------")

if __name__ == "__main__":
    main()
