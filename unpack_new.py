#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess

# Constants
HDIFF_DIR = "./Hdiff Files"
ORIGINAL_DIR = "./Original Game Files"
NEW_DIR = "./New Game Files"
WAV_DIR = "./WAV"

TOOLS_DIR = "./Tools"
ORIGINAL_DECODE_DIR = "./Tools/Original Decoding"
NEW_DECODE_DIR = "./Tools/New Decoding"

# Check if running on Windows and append .exe if so
EXECUTABLE_EXTENSION = ""
if os.name == 'nt':
    EXECUTABLE_EXTENSION = ".exe"

# Walk directory and return list of .hdiff files in root of directory
def walk_dir(path):
    file_list = []
    # Get file list at root of path
    for (dirpath, dirnames, filenames) in os.walk(path):
        file_list.extend(filenames)
        break
    return list(filter(lambda name: Path(name).suffix == ".hdiff", file_list))

# Run hpatch for all hdiff files listed in file_list
# Patches files in original_dir with patches in patch_dir and output result to output_dir
def hpatch_files(original_dir, patch_dir, output_dir, file_list):
    hpatch_exec = Path.joinpath(Path(TOOLS_DIR).resolve(), "hpatchz" + EXECUTABLE_EXTENSION)
    original_dir_abs = Path(original_dir).resolve()
    patch_dir_abs = Path(patch_dir).resolve()
    output_dir_abs = Path(output_dir).resolve()
    for file_name in file_list:
        # Get original file name without .hdiff extension
        file_name_stem = Path(file_name).stem
        subprocess.call([hpatch_exec, Path.joinpath(original_dir_abs, file_name_stem), Path.joinpath(patch_dir_abs, file_name), Path.joinpath(output_dir_abs, file_name_stem)])

# Extract individual audio files from Wwise PCK files with quickbms
def extract_files(original_dir, output_dir):
    tools_dir_abs = Path(TOOLS_DIR).resolve()
    subprocess.call([Path.joinpath(tools_dir_abs, "quickbms" + EXECUTABLE_EXTENSION), Path.joinpath(tools_dir_abs, "wavescan.bms"), Path(original_dir).resolve(), Path(output_dir).resolve()])

# Find and return list of all files in new_dir that are not also present in original_dir
def filter_diff_files(original_dir, new_dir):
    original_dir_abs = Path(original_dir).resolve()
    new_dir_abs = Path(new_dir).resolve()
    # Get list of all patched files
    patched_file_list = []
    for (dirpath, dirnames, filenames) in os.walk(new_dir):
        patched_file_list.extend(filenames)
        break
    patched_file_list = list(filter(lambda name: Path(name).suffix == ".wem", patched_file_list))
    # Calculate list of new files
    new_file_list = []
    # Iterate over all patched files to find ones that weren't present before
    for file_name in patched_file_list:
        old_file = Path.joinpath(original_dir_abs, file_name)
        new_file = Path.joinpath(new_dir_abs, file_name)
        # If file name exised in old directory, check sizes
        if old_file.exists():
            old_file_size = old_file.stat().st_size
            new_file_size = new_file.stat().st_size
            if old_file_size != new_file_size:
                new_file_list.append(file_name)
        # If file didn't exist in old directory, add to new list
        else:
            new_file_list.append(file_name)
    return new_file_list

# Convert all files from file_dir with names in file_list to WAV format
def convert_to_wav(file_dir, file_list, output_dir):
    vgmstream_exec = Path.joinpath(Path(TOOLS_DIR).resolve(), "vgmstream-cli" + EXECUTABLE_EXTENSION)
    file_dir_abs = Path(file_dir).resolve()
    output_dir_abs = Path(output_dir).resolve()
    for file_name in file_list:
        file = Path.joinpath(file_dir_abs, file_name)
        output_file = Path.joinpath(output_dir_abs, file.stem + ".wav")
        subprocess.call([vgmstream_exec, "-o", output_file, file])

def main():
    file_list = walk_dir(HDIFF_DIR) # Gets list of all .hdiff files
    hpatch_files(ORIGINAL_DIR, HDIFF_DIR, NEW_DIR, file_list) # Patch all Wwise PCK audio files
    extract_files(ORIGINAL_DIR, ORIGINAL_DECODE_DIR) # Extract all original audio files
    extract_files(NEW_DIR, NEW_DECODE_DIR) # Extract all patched audio files
    new_file_list = filter_diff_files(ORIGINAL_DECODE_DIR, NEW_DECODE_DIR) # Find any new audio files that were not present in original PCK
    convert_to_wav(NEW_DECODE_DIR, new_file_list, WAV_DIR) # Convert all new audio files to WAV

if __name__ == "__main__":
    main()
