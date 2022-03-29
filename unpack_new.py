#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess
import hashlib

# Constants
MD5_HASH_FILES = True

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
    total = len(file_list)
    iteration = 0
    for file_name in file_list:
        iteration += 1
        show_progress(iteration, total, "", "Patching Files")
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
    for (dirpath, dirnames, filenames) in os.walk(new_dir):
        new_file_list.extend(filenames)
        break
    new_file_list = list(filter(lambda name: Path(name).suffix == ".wem", new_file_list))
    return_list = []
    total = len(original_file_list) + len(new_file_list)
    iteration = 0
    if MD5_HASH_FILES:
        old_file_hashes = {}
        new_file_hashes = {}
        for file_name in original_file_list:
            iteration += 1
            show_progress(iteration, total, "", "Filtering New Files")
            old_file = Path.joinpath(original_dir_abs, file_name)
            file_hash = get_md5(old_file)
            if file_hash:
                old_file_hashes[file_hash + "," + str(old_file.stat().st_size)] = file_name
        for file_name in new_file_list:
            iteration += 1
            show_progress(iteration, total, "", "Filtering New Files")
            new_file = Path.joinpath(new_dir_abs, file_name)
            file_hash = get_md5(new_file)
            if file_hash:
                new_file_hashes[file_hash + "," + str(new_file.stat().st_size)] = file_name
            else:
                return_list.append(file_name)
        diff_keys = set(new_file_hashes.keys()) - set(old_file_hashes.keys())
        total = len(diff_keys)
        iteration = 0
        for key in diff_keys:
            iteration += 1
            show_progress(iteration, total, "", "Finalizing")
            return_list.append(new_file_hashes[key])
    else:
        for file_name in new_file_list:
            iteration += 1
            show_progress(iteration, total, "", "Filtering New Files")
            if file_name not in original_file_list:
                return_list.append(file_name)
        for file_name in original_file_list:
            iteration += 1
            show_progress(iteration, total, "", "Filtering New Files")
            old_file = Path.joinpath(original_dir_abs, file_name)
            new_file = Path.joinpath(new_dir_abs, file_name)
            if new_file.exists():
                old_file_size = old_file.stat().st_size
                new_file_size = new_file.stat().st_size
                if old_file_size != new_file_size:
                    return_list.append(file_name)
    return return_list

def get_md5(file):
    try:
        return hashlib.md5(file.read_bytes()).hexdigest()
    except:
        return False

def convert_to_wav(file_dir, file_list, output_dir):
    total = len(file_list)
    iteration = 0
    file_dir_abs = Path(file_dir).resolve()
    output_dir_abs = Path(output_dir).resolve()
    for file_name in file_list:
        iteration += 1
        show_progress(iteration, total, "", "Converting to WAV")
        file = Path.joinpath(file_dir_abs, file_name)
        output_file = Path.joinpath(output_dir_abs, file.stem + ".wav")
        subprocess.call([Path.joinpath(Path(TOOLS_DIR).resolve(), "vgmstream-cli" + EXECUTABLE_EXTENSION), "-o", output_file, file])

def show_progress(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def main():
    file_list = walk_dir(HDIFF_DIR)
    hpatch_files(ORIGINAL_DIR, HDIFF_DIR, NEW_DIR, file_list)
    extract_files(ORIGINAL_DIR, ORIGINAL_DECODE_DIR)
    extract_files(NEW_DIR, NEW_DECODE_DIR)
    new_file_list = filter_diff_files(ORIGINAL_DECODE_DIR, NEW_DECODE_DIR)
    convert_to_wav(NEW_DECODE_DIR, new_file_list, WAV_DIR)

if __name__ == "__main__":
    main()