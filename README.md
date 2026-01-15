

# UniCompare
```text
   __  __      _ ______
  / / / /___  (_) ____/___  ____ ___  ____  ____ _________
 / / / / __ \/ / /   / __ \/ __ `__ \/ __ \/ __ `/ ___/ _ \
/ /_/ / / / / / /___/ /_/ / / / / / / /_/ / /_/ / /  /  __/
\____/_/ /_/_/\____/\____/_/ /_/ /_/ .___/\__,_/_/   \___/
                                  /_/
```
**Automated Output Comparison & Memory Testing for Students**

</div>

---

## 📖 Overview

**UniCompare** is a CLI tool designed to help university students test their coursework. It runs two executables side-by-side, feeds them input files, and compares their standard output. It now includes **Valgrind** integration for memory leak detection and **Beyond Compare** support for visual diffs.

## ✨ Features

* 🎯 **Precision Comparison**: Instantly diff stdout between two programs.
* 🧠 **Memory Safety**: Automatic **Valgrind** integration to catch memory leaks.
* 📂 **Recursive Testing**: deeply scans directories for input files (default: 5 levels).
* ⚔️ **Visual Diffs**: Opens mismatched files directly in **Beyond Compare**.
* ⏱️ **Timeout Guard**: Kills infinite loops automatically (default: 5s).
* 🚀 **Argument Support**: Pass arguments directly to your executables.
* 💾 **Auto-Save**: Mismatches and Valgrind reports are saved for review.

---

## ⚙️ Installation

### 🆕 Beginner's Helper: Setup Virtual Environment

If you are new to Python or getting "Externally Managed Environment" errors, follow these steps first:

1. **Create the virtual environment** (run once):
```bash
python3 -m venv myvenv

```


2. **Activate it** (run this every time you open a new terminal):
* **Linux / Mac / WSL:**
```bash
source myvenv/bin/activate

```


* **Windows (Command Prompt):**
```cmd
myvenv\Scripts\activate

```


* **Windows (PowerShell):**
```powershell
.\myvenv\Scripts\Activate.ps1

```




3. **Verify:** You should see `(myvenv)` at the start of your command line. Now you are ready to install!

### 1. Python Dependencies

Once your environment is active, install the required libraries:

```bash
pip install colorama pyfiglet

```

### 2. External Tools (Optional)

| Tool | Windows | Linux | Usage |
| --- | --- | --- | --- |
| **Beyond Compare** | [Download Installer](https://www.scootersoftware.com/download.php) | `sudo apt install bcompare` | Visual diffs |
| **Valgrind** | Use WSL (Ubuntu) | `sudo apt install valgrind` | Memory checks |

---

## 🚀 Usage

### Basic Syntax

```bash
unic <exec1> <exec2> --files <inputs> [options]

```

### Common Scenarios

#### 🟢 Simple Comparison

Compare `program1` and `program2` with a single input file:

```bash
unic ./program1 ./program2 -f input.txt

```

#### 🟡 Passing Arguments

If your programs need command-line arguments (e.g., `./solver 100 20`), **wrap the command in quotes**:

```bash
unic "./solver 100 20" "./student_sol 100 20" -f tests/input.txt

```

#### 🔴 Memory Leak Check

Run tests and check for memory leaks using Valgrind:

```bash
unic ./prog1 ./prog2 -f tests/ --valgrind

```

#### 🔵 Custom Settings

Save results to a specific folder and set a strict timeout:

```bash
unic ./prog1 ./prog2 -f tests/ --output my_report --timeout 2

```

---

## 📊 Output Example

When running tests, UniCompare provides clear, color-coded feedback:

```text
============================================================
Running tests on 4 file(s)...
============================================================

[✓] tests/basic/simple.txt
[✗] tests/advanced/hard.txt (Output Mismatch)
[M] tests/memory/leak_test.txt (Memory Error)
    ↳ Memory leaks in Exec 1
[T] tests/infinite_loop.txt (Timeout)

============================================================
Results saved in uniTestResults/ folder
============================================================

```

---

## 🔧 Configuration & Arguments

| Flag | Short | Description | Default |
| --- | --- | --- | --- |
| `--files` | `-f` | **(Required)** List of input files or directories to scan. | - |
| `--output` | `-o` | Directory to save mismatched output/logs. | `uniTestResults` |
| `--valgrind` | `-v` | Run inside Valgrind to detect memory errors. | `False` |
| `--timeout` | `-t` | Max execution time (seconds) per test. | `5.0` |
| `--max-depth` | `-d` | Max recursion depth for directory scanning. | `5` |

---

### 🚦 Status Legend

| Icon | Status | Description |
| :---: | --- | --- |
| `[✓]` | **PASS** | Output matches exactly between both programs. |
| `[✗]` | **FAIL** | Output mismatch. Diff saved to results folder. |
| `[M]` | **LEAK** | Output matched, but Valgrind detected memory errors. |
| `[T]` | **TIMEOUT** | Program took longer than the configured limit (killed). |

---
## 📂 File Structure

When a test fails, results are organized automatically:

```text
uniTestResults/
├── tests/advanced/hard.txt/
│   ├── prog1_output.txt        # Stdout of program 1
│   └── prog2_output.txt        # Stdout of program 2
└── tests/memory/leak_test.txt/
    ├── prog1_valgrind.txt      # Valgrind error report
    └── ...

```

---

## 👥 Authors

* **Denis Irkl**
* **Naor Biton**

---
