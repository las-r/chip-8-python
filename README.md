![Screenshot showing the IBM Logo in the emulator.](https://github.com/user-attachments/assets/5e3f1507-bfd3-474e-92f8-c6faf5c71a34)

# CHIP-8 Python
A CHIP-8 emulator written in Python.

## Usage
How to actually use the emulator.
#### Shell
```
python emu.py ROMFILE [arguments]
```
### Arguments
|Argument|Action|Type|
|-|-|-|
|`-h`|Get help menu|N/A|
|`--debug`|Debug level (default: 0)|Integer|
|`--legacy-bit-shift`|Use legacy bit shift behavior|Boolean|
|`--legacy-offset-jump`|Use legacy offset jump behavior|Boolean|
|`--legacy-store`|Use legacy memory store behavior|Boolean|
|`--hz`|Instructions executed per second (default: 700)|Integer|
|`--width`|Display width in pixels (default: 512)|Integer|
|`--height`|Display height in pixels (default: 256)|Integer|

## Resources Used
Resources used in the development and testing of the emulator.
- https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
- https://github.com/Timendus/chip8-test-suite
- https://github.com/badlogic/chip8/

## Credits
ROM used in screenshot is acquired from [Timendus' CHIP-8 Test Suite](https://github.com/Timendus/chip8-test-suite).
