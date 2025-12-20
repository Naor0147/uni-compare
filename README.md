# UniCompare

A simple program to help university students manage their coursework. Given 2 executable files, it will run them and compare their outputs with the given input file/s.

## Features

- ✅ Compare outputs of two executable programs
- 📁 Recursive directory traversal with configurable depth (default: 5 levels)
- 🔍 Smart duplicate file handling with indexed naming
- 🔄 Cross-platform support (Windows/Linux)
- 🎨 Colorized output with status indicators
- 📊 Integration with Beyond Compare for visual diff
- 💾 Automatic result saving for mismatched outputs

## Installation


### Beyond Compare

For visual diff functionality, install Beyond Compare:

**Windows:**
- Download from: https://www.scootersoftware.com/download.php
- Default installation path: `C:\Program Files\Beyond Compare 4`

**Linux (Ubuntu/Debian):**
- Will be automatically installed when first needed
- Or manually: `sudo apt install bcompare`

## Usage

### Basic Syntax

```bash
unic <executable1> <executable2> --files <input_files...> [--max-depth <depth>]
```

### Examples

#### Compare two programs with single input file

```bash
unic program1.exe program2.exe --files input.txt
```

#### Compare with multiple input files

```bash
unic ./solution1 ./solution2 -f test1.txt test2.txt test3.txt
```

#### Compare using directory (recursive)

```bash
unic program1.exe program2.exe --files tests/
```

#### Compare with custom max depth

```bash
unic program1.exe program2.exe --files tests/ --max-depth 3
```

This will recursively search for `.txt` files up to 5 directory levels deep (default):
```
tests/
├── input1.txt          ✅ Found
├── subdir1/
│   ├── input2.txt      ✅ Found
│   └── deeper/
│       ├── input3.txt  ✅ Found
│       └── level3/
│           ├── input4.txt  ✅ Found
│           └── level4/
│               ├── input5.txt  ✅ Found
│               └── level5/
│                   └── input6.txt  ❌ Too deep (level 6)
```

#### Mixed files and directories

```bash
unic solver1.exe solver2.exe -f single.txt tests/ more_tests/
```

## Output Examples

### Successful Comparison
```
==========================================
Running tests on 3 file(s)...
==========================================

[✓] tests/basic/input1.txt
[✓] tests/basic/input2.txt
[✓] tests/edge/special.txt

==========================================
All tests passed! No mismatches found.
==========================================
```

### With Mismatches and Duplicates
```
==========================================
Running tests on 5 file(s)...
==========================================

[✓] tests/basic/simple.txt[1]
[✗] tests/advanced/simple.txt[2]
[✗] tests/edge/simple.txt[3]
[✓] tests/other/unique.txt
[✗] manual_test.txt

==========================================
Results saved in results/ folder
==========================================

Which input file would you like to view the differences for?
(Type 'exit' to quit)
Available files:
  - simple.txt[1]
  - simple.txt[2]
  - simple.txt[3]
  - manual_test.txt

Enter filename: simple.txt[2]
```

## File Organization

### Results Structure

When mismatches occur, results are saved in the `results/` folder:

```
results/
├── tests/advanced/simple.txt/
│   ├── program1.txt          # Output from first executable
│   └── program2.txt          # Output from second executable
├── tests/edge/simple.txt/
│   ├── program1.txt
│   └── program2.txt
└── manual_test.txt/
    ├── program1.txt
    └── program2.txt
```

### Duplicate File Handling

Files with the same basename in different directories are handled intelligently:

**Input Structure:**
```
tests/
├── basic/simple.txt
├── advanced/simple.txt
└── edge/simple.txt
```

**Display Names:**
- `tests/basic/simple.txt[1]`
- `tests/advanced/simple.txt[2]`
- `tests/edge/simple.txt[3]`

**User Input:** Just type `simple.txt[2]` to select the specific file.

## Command Line Arguments

| Argument | Description | Required | Example |
|----------|-------------|----------|---------|
| `exec1` | Path to first executable | ✅ | `./program1` |
| `exec2` | Path to second executable | ✅ | `./program2` |
| `--files`, `-f` | Input files/directories | ✅ | `-f test1.txt dir/` |
| `--max-depth`, `-d` | Max directory depth for recursion | ❌ | `-d 3` (default: 5) |

## Interactive Mode

After running comparisons, if mismatches are found, you enter interactive mode:

```
Which input file would you like to view the differences for?
(Type 'exit' to quit)
Enter filename: simple.txt[2]
```

### Commands:
- Enter any filename from the "Available files" list
- Type `exit` to quit
- `Ctrl+C` to interrupt

## Beyond Compare Integration

When you select a mismatched file, UniCompare automatically:

1. **Windows**: Launches `bcomp.exe` from `PATH` with the two output files
2. **Linux**: Launches `bcompare` binary with the two output files

If Beyond Compare isn't found:
- **Windows**: Provides installation instructions and adds default installation folder to `PATH`
- **Linux**: Automatically downloads and installs it using apt package manager

## Error Handling

### Common Issues

**File Not Found:**
```
[✗] missing_file.txt (FILE/DIRECTORY NOT FOUND)
```

**Permission Errors:**
- Automatically skipped during directory traversal
- No interruption to the comparison process

## Technical Details

### File Processing
- Reads entire input file into memory
- Pipes input to both executables via stdin
- Captures stdout from both programs
- Compares outputs using string equality

### Directory Traversal
- Uses `os.path.isfile()` and `os.path.isdir()` for type detection
- Recursively processes subdirectories up to configurable depth (default: 5)
- Only processes files with `.txt` extension
- Gracefully handles permission errors

### Cross-Platform Support
- Uses `subprocess.Popen()` for reliable process execution
- Handles Windows `.exe` extension automatically
- Path normalization for consistent results display

## Authors

Denis Irkl (6'1 180lbs lean btw)
Claude Sonnet 4 & Github Copilot Pro ❤️

---

*Made for university students who need to compare program outputs efficiently.*
