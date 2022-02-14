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

EXECUTABLE_EXTENSION = ""
if os.name == 'nt':
    EXECUTABLE_EXTENSION = ".exe"

def walk_dir(path):
    file_list = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        file_list.extend(filenames)
        break
    return list(filter(lambda name: Path(name).suffix == ".hdiff", file_list))

def hpatch_files(original_dir, patch_dir, output_dir, file_list):
    hpatch_exec = Path.joinpath(Path(TOOLS_DIR).resolve(), "hpatchz" + EXECUTABLE_EXTENSION)
    original_dir_abs = Path(original_dir).resolve()
    patch_dir_abs = Path(patch_dir).resolve()
    output_dir_abs = Path(output_dir).resolve()
    for file_name in file_list:
        file_name_stem = Path(file_name).stem
        subprocess.call([hpatch_exec, Path.joinpath(original_dir_abs, file_name_stem), Path.joinpath(patch_dir_abs, file_name), Path.joinpath(output_dir_abs, file_name_stem)])

def extract_files(original_dir, output_dir):
    tools_dir_abs = Path(TOOLS_DIR).resolve()
    subprocess.call([Path.joinpath(tools_dir_abs, "quickbms" + EXECUTABLE_EXTENSION), Path.joinpath(tools_dir_abs, "wavescan.bms"), Path(original_dir).resolve(), Path(output_dir).resolve()])

def filter_diff_files(original_dir, new_dir):
    original_dir_abs = Path(original_dir).resolve()
    new_dir_abs = Path(new_dir).resolve()
    original_file_list = []
    for (dirpath, dirnames, filenames) in os.walk(original_dir):
        original_file_list.extend(filenames)
        break
    original_file_list = list(filter(lambda name: Path(name).suffix == ".wem", original_file_list))
    new_file_list = []
    for file_name in original_file_list:
        old_file = Path.joinpath(original_dir_abs, file_name)
        new_file = Path.joinpath(new_dir_abs, file_name)
        if new_file.exists():
            old_file_size = old_file.stat().st_size
            new_file_size = new_file.stat().st_size
            if old_file_size != new_file_size:
                new_file_list.append(file_name)
    return new_file_list

def convert_to_wav(file_dir, file_list, output_dir):
    file_dir_abs = Path(file_dir).resolve()
    output_dir_abs = Path(output_dir).resolve()
    for file_name in file_list:
        file = Path.joinpath(file_dir_abs, file_name)
        output_file = Path.joinpath(output_dir_abs, file.stem + ".wav")
        subprocess.call([Path.joinpath(Path(TOOLS_DIR).resolve(), "vgmstream-cli" + EXECUTABLE_EXTENSION), "-o", output_file, file])

def main():
    file_list = walk_dir(HDIFF_DIR)
    hpatch_files(ORIGINAL_DIR, HDIFF_DIR, NEW_DIR, file_list)
    extract_files(ORIGINAL_DIR, ORIGINAL_DECODE_DIR)
    extract_files(NEW_DIR, NEW_DECODE_DIR)
    new_file_list = filter_diff_files(ORIGINAL_DECODE_DIR, NEW_DECODE_DIR)
    convert_to_wav(NEW_DECODE_DIR, new_file_list, WAV_DIR)

if __name__ == "__main__":
    main()