# Genshin Impact Hdiff Music Unpacker
Uses Hdiff to patch game music files, then searches through files to find any new music and decodes it to WAV.

Based on Wwise Unpacker https://github.com/Vextil/Wwise-Unpacker

Here's the archive structure:

* Unpacker
  * Hdiff Files (HDIFF files) (Diff files from update zip)
  * New Game Files (PCK files) (Leave this empty - it will contain the patched files after running)
  * Original Game Files (PCK files) (Old game files from current release)
  * Tools (Tools used for the unpacking process)
  * WAV (WAV file output)