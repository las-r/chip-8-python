![Screenshot showing the IBM Logo in the emulator.](https://github.com/user-attachments/assets/5e3f1507-bfd3-474e-92f8-c6faf5c71a34)

# CHIP-8 Python
A CHIP-8 emulator written in Python.

## Usage
How to actually use the emulator.
#### Shell
```
python emu.py FILE.ch8 [arguments]
```
### Arguments
|Argument|Action|
|-|-|
|`-h`|Get help menu|
|`--debug`|Enable debug mode|
|`--legacy-bit-shift`|Use legacy bit shift behavior|
|`--legacy-offset-jump`|Use legacy offset jump behavior|
|`--legacy-store`|Use legacy memory store behavior|
|`--hz`|Instructions executed per second (default: 700)|
|`--width`|Display width in pixels (default: 512)|
|`--height`|Display height in pixels (default: 256)|

## Resources Used
Resources used in the development and testing of the emulator.
- https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
- https://github.com/Timendus/chip8-test-suite
- https://github.com/badlogic/chip8/
