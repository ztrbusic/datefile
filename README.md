# DATEFILE v0.1.0

A small Python CLI tool that renames photos and videos based on their capture date using ExifTool or filename information. Built for clean, predictable media organisation.

This is just an initial version that can only _read_ exif and filenames and report. Actual renaming will probably come in v.0.3.0.

### Features
- Extracts capture date from EXIF metadata
- Supports common photo and video formats
- Optional recursive processing

### Coming soon
- Dry-run option
- Manifest after renaming for safe reversal
- Actual renaming functionality

## Installation
`brew install exiftool` - needed for EXIF processing

`pip install -e .` - installs in editable mode during development

## Usage
Basic:
`datefile scan path/to/folder`

For recursive add `--recursive` or `-r` BEFORE path

## Future renaming example
Before:  
IMG_8392.jpg  
VID_20230504_183200.mp4  

After:  
2023-05-04_18-32-00.jpg  
2023-05-04_18-32-00.mp4