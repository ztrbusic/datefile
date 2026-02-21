from pathlib import Path
import typer
from rich import print
from datetime import datetime
import re
import subprocess
from PIL import Image, ExifTags

# --- Date from filename -----------------------------------------------------------

def date_from_filename(stem: str) -> datetime | None:
    """Extract a capture datetime from known filename patterns."""
    # Pattern A: YYYYMMDD_HHMMSS
    match = re.match(r"^(\d{8})_(\d{6})", stem)
    if match:
        date_part = match.group(1)  # YYYYMMDD
        time_part = match.group(2)  # HHMMSS
        return datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
    return None

# --- Date from exiftool ---------------------------------------------------------------

EXIFTOOL_TAGS = [
    # Photos (best)
    "DateTimeOriginal",
    "CreateDate",
    # Videos (MP4)
    "MediaCreateDate",
    "TrackCreateDate",
    # Fallback-ish (still inside file metadata, not filesystem)
    "ModifyDate",
    "MediaModifyDate",
    "TrackModifyDate",
    # Uncomment ONLY if you decide to accept filesystem as last resort:
    "FileModifyDate",
]

EXIFTOOL_DT_FORMATS = (
    "%Y:%m:%d %H:%M:%S.%f%z",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y:%m:%d %H:%M:%S.%f",
    "%Y:%m:%d %H:%M:%S",
)

def parse_exiftool_dt(value: str) -> datetime | None:
    for fmt in EXIFTOOL_DT_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass
    return None

def exiftool_value(file: Path, tag: str) -> str:
    cmd = [
        "exiftool",
        "-s", "-s", "-s",           # value only
        "-api", "QuickTimeUTC=1",   # consistent MP4 handling
        f"-{tag}",
        str(file),
    ]
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except FileNotFoundError:
        raise RuntimeError("exiftool not found. Install with: brew install exiftool")
    except subprocess.CalledProcessError:
        return ""

def datetime_from_exiftool(file: Path) -> tuple[datetime, str] | None:
    for tag in EXIFTOOL_TAGS:
        value = exiftool_value(file, tag)
        if not value:
            continue
        dt = parse_exiftool_dt(value)
        if dt is not None:
            return dt, tag
    return None

# --- Capture: EXIF or Filename -----------------------------------------

def capture_datetime(file: Path) -> tuple[datetime, str]:
    """Source is filename or exiftool:<tag>."""
    dt = date_from_filename(file.stem)
    if dt is not None:
        return dt, "filename"

    result = datetime_from_exiftool(file)
    if result is not None:
        dt, tag = result
        return dt, f"exiftool: {tag}"

    raise ValueError(f"No valid date found for {file.name}")

# --- CLI ---------------------------------------------------------------

app = typer.Typer()

@app.callback()
def cli():
    """
    Datefile is a command-line tool for scanning, renaming and sorting image
    and video files according to date.
    """
    pass

@app.command(name="scan", help="Tool for scanning for images and videos")
def scan(
    folder: Path,
    recursive: bool = typer.Option(
        False,
        "--recursive", "-r",
        help = "Scan directories recursively"
        )
    ):
    # Scan the files
    if not folder.exists():
        print("[red]Folder does not exist.[/red]")
        raise typer.Exit()
    files = list(folder.rglob("*") if recursive else folder.iterdir())
    media = [
        f for f in files
        if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".mp4"}
        ]
    print(f"[green]Found {len(media)} media files.[/green]")
    if len(media) > 0:
        print("First 10 media files in the folder are:")
        for med in media[:10]:
            print(" -", med.name)

    # Datetime capture test
    print("\nDatetime capture test:")
    for f in media:
        dt = capture_datetime(f)
        print(f" - {f.name} -> {dt}")

@app.command()
def rename():
    """Rename files (coming soon)."""
    raise typer.Exit(code=0)