import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

from colorama import Fore, Style, init
from pyfiglet import Figlet

init(autoreset=True)

parser = argparse.ArgumentParser(
    description="A simple program to help university students manage their coursework. Given 2 executable files, it will run them and compare their outputs with the given input file/s."
)

parser.add_argument("exec1", help="Path to the first executable file.")
parser.add_argument("exec2", help="Path to the second executable file.")
parser.add_argument(
    "--files",
    "-f",
    nargs="+",
    help="List of input files to test the executables with.",
    required=True,
)


def process_file(input_file, exec1, exec2, display_name=None):
    # Convert to absolute paths
    exec1_path = os.path.abspath(exec1)
    exec2_path = os.path.abspath(exec2)

    # Use display_name if provided, otherwise use input_file
    display_text = display_name if display_name else input_file

    # Read input file
    try:
        with open(input_file, "r") as f:
            input_data = f.read()
    except IOError as e:
        print(
            f"{Fore.RED}Error reading input file {display_text}: {e}{Style.RESET_ALL}"
        )
        return False, "", ""

    # Run executables with subprocess for proper cross-platform handling
    try:
        proc1 = subprocess.Popen(
            [exec1_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output1, _ = proc1.communicate(input=input_data)

        proc2 = subprocess.Popen(
            [exec2_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output2, _ = proc2.communicate(input=input_data)
    except Exception as e:
        print(f"{Fore.RED}Error running executables: {e}{Style.RESET_ALL}")
        return False, "", ""

    if output1 == output2:
        print(f"{Fore.GREEN}[✓] {display_text}{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}[✗] {display_text}{Style.RESET_ALL}")
        return False, output1, output2


def save_mismatched_outputs(input_file, output1, output2, exec1, exec2):
    """Save outputs for mismatched files to results folder."""
    try:
        # Create a unique results folder using relative path (replace separators to avoid nested folders)
        rel_path = os.path.normpath(input_file).replace("\\", "/").replace(":", "")
        results_dir = os.path.join("results", rel_path)
        Path(results_dir).mkdir(parents=True, exist_ok=True)

        # Get executable names without path
        exec1_name = os.path.basename(exec1).replace(".exe", "") + ".txt"
        exec2_name = os.path.basename(exec2).replace(".exe", "") + ".txt"

        # Save outputs
        with open(os.path.join(results_dir, exec1_name), "w") as f:
            f.write(output1)

        with open(os.path.join(results_dir, exec2_name), "w") as f:
            f.write(output2)
    except IOError as e:
        print(f"{Fore.RED}Error saving results for {input_file}: {e}{Style.RESET_ALL}")


def handle_windows_beyond_compare():
    """Handle Beyond Compare setup for Windows."""
    default_path = r"C:\Program Files\Beyond Compare 4\bcomp.exe"

    if os.path.exists(default_path):
        print(f"{Fore.GREEN}Found Beyond Compare at default location.{Style.RESET_ALL}")
        # Add to PATH
        os.environ["PATH"] += f";{os.path.dirname(default_path)}"
        return True
    else:
        print(
            f"{Fore.YELLOW}Beyond Compare not found at default location.{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}To fix this, please:")
        print(
            f"1. Install Beyond Compare from: https://www.scootersoftware.com/download.php{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}2. The default installation path is: C:\\Program Files\\Beyond Compare 4{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}3. Or add Beyond Compare to your system PATH environment variable.{Style.RESET_ALL}"
        )
        return False


def handle_linux_beyond_compare():
    """Handle Beyond Compare setup for Linux."""
    print(f"{Fore.YELLOW}Installing Beyond Compare...{Style.RESET_ALL}")

    deb_file = "bcompare-5.1.7.31736_amd64.deb"
    commands = [
        f"wget https://www.scootersoftware.com/files/{deb_file}",
        "sudo apt update",
        f"sudo apt install -y ./{deb_file}",
        f"rm -f {deb_file}",
    ]

    try:
        for cmd in commands:
            print(f"{Fore.CYAN}Running: {cmd}{Style.RESET_ALL}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Fore.RED}Error: {result.stderr}{Style.RESET_ALL}")
                return False

        print(f"{Fore.GREEN}Beyond Compare installed successfully!{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error installing Beyond Compare: {e}{Style.RESET_ALL}")
        return False


def open_in_beyond_compare(results_dir):
    """Open Beyond Compare with the comparison files."""
    exec1_file = None
    exec2_file = None

    # Find the two output files
    for file in os.listdir(results_dir):
        if file.endswith(".txt"):
            if exec1_file is None:
                exec1_file = os.path.join(results_dir, file)
            else:
                exec2_file = os.path.join(results_dir, file)
                break

    if not exec1_file or not exec2_file:
        print(
            f"{Fore.RED}Error: Could not find both output files in {results_dir}{Style.RESET_ALL}"
        )
        return

    # Determine the command based on OS
    if platform.system() == "Windows":
        cmd = ["bcomp.exe", exec1_file, exec2_file]
    else:  # Linux and macOS
        cmd = ["bcompare", exec1_file, exec2_file]

    try:
        subprocess.Popen(cmd)
    except FileNotFoundError:
        print(
            f"{Fore.YELLOW}Beyond Compare not found. Attempting to set up Beyond Compare...{Style.RESET_ALL}"
        )

        # Attempt OS-specific installation/setup
        if platform.system() == "Windows":
            setup_success = handle_windows_beyond_compare()
        else:
            setup_success = handle_linux_beyond_compare()

        if setup_success:
            # Retry opening Beyond Compare
            print(f"{Fore.CYAN}Retrying to open Beyond Compare...{Style.RESET_ALL}")
            try:
                subprocess.Popen(cmd)
                print(f"{Fore.GREEN}Opening Beyond Compare...{Style.RESET_ALL}")
            except FileNotFoundError:
                print(
                    f"{Fore.RED}Failed to open Beyond Compare even after setup. Please install it manually and try again.{Style.RESET_ALL}"
                )
                print(f"{Fore.RED}Program will now exit.{Style.RESET_ALL}")
                sys.exit(1)
        else:
            print(
                f"{Fore.RED}Failed to set up Beyond Compare. Please install it manually and try again.{Style.RESET_ALL}"
            )
            print(f"{Fore.RED}Program will now exit.{Style.RESET_ALL}")
            sys.exit(1)


def get_txt_files_recursive(directory, max_depth=3):
    """Recursively find all .txt files up to max_depth directories deep."""
    txt_files = []

    def traverse(path, current_depth):
        if current_depth > max_depth:
            return

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and item.endswith(".txt"):
                    txt_files.append(item_path)
                elif os.path.isdir(item_path):
                    traverse(item_path, current_depth + 1)
        except PermissionError:
            pass

    traverse(directory, 1)
    return txt_files


def interactive_compare_loop(mismatched_files):
    """Interactive loop to view mismatches in Beyond Compare."""
    # Build a mapping of display names (with numbers) to results paths
    basename_count = {}
    file_mapping = {}  # maps display name (e.g., "a.txt[1]") to results path

    for full_path in mismatched_files:
        basename = os.path.basename(full_path)

        # Count occurrences of each basename
        if basename not in basename_count:
            basename_count[basename] = 0
        basename_count[basename] += 1

    # Create display names with numbers for duplicates
    basename_seen = {}
    for full_path in mismatched_files:
        basename = os.path.basename(full_path)
        rel_path = os.path.normpath(full_path).replace("\\", "/").replace(":", "")
        results_path = os.path.join("results", rel_path)

        if basename_count[basename] > 1:
            # Multiple files with same name, add number
            if basename not in basename_seen:
                basename_seen[basename] = 0
            basename_seen[basename] += 1
            display_name = f"{basename}[{basename_seen[basename]}]"
        else:
            # Unique name, no number needed
            display_name = basename

        file_mapping[display_name] = results_path

    while True:
        try:
            print(
                f"\n{Fore.CYAN}Which input file would you like to view the differences for?{Style.RESET_ALL}"
            )
            print(f"{Fore.CYAN}(Type 'exit' to quit){Style.RESET_ALL}")

            user_input = input(f"{Fore.CYAN}Enter filename: {Style.RESET_ALL}").strip()

            if user_input.lower() == "exit":
                print(f"{Fore.GREEN}Exiting...{Style.RESET_ALL}")
                break

            if not user_input:
                print(f"{Fore.YELLOW}Please enter a valid filename.{Style.RESET_ALL}")
                continue

            # Check if the file exists in mapping
            if user_input not in file_mapping:
                print(
                    f"{Fore.RED}Error: '{user_input}' not found in results.{Style.RESET_ALL}"
                )
                print(f"{Fore.YELLOW}Available files:{Style.RESET_ALL}")
                for display_name in sorted(file_mapping.keys()):
                    print(f"  - {display_name}")
                continue

            results_path = file_mapping[user_input]
            open_in_beyond_compare(results_path)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted by user. Exiting...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")


def main():
    args = parser.parse_args()

    exec1 = args.exec1
    exec2 = args.exec2
    input_files = args.files

    has_output_mismatches = False
    mismatched_files = []

    # Display ASCII art banner
    fig = Figlet(font="slant")
    banner = fig.renderText("UniCompare")
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{banner}{Style.RESET_ALL}")

    description = "A simple program to help university students manage their coursework.\nGiven 2 executable files, it will run them and compare their outputs with the given input file/s."
    print(f"{Fore.YELLOW}{description}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Author: Denis Irkl (6'1 180lbs lean){Style.RESET_ALL}\n")

    print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
    print(
        f"{Style.BRIGHT}Running tests on {len(input_files)} file(s)...{Style.RESET_ALL}"
    )
    print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}\n")

    # First pass: collect all files and build basename count
    all_files = []
    basename_count = {}

    for input_file in input_files:
        if not os.path.exists(input_file):
            continue

        if os.path.isdir(input_file):
            txt_files = get_txt_files_recursive(input_file)
            all_files.extend(txt_files)
        else:
            all_files.append(input_file)

    # Count how many files share the same basename
    for file_path in all_files:
        basename = os.path.basename(file_path)
        basename_count[basename] = basename_count.get(basename, 0) + 1

    # Second pass: process files with correct display names
    basename_indices = {}

    for input_file in input_files:
        if not os.path.exists(input_file):
            print(
                f"{Fore.RED}[✗] {input_file} (FILE/DIRECTORY NOT FOUND){Style.RESET_ALL}"
            )
            continue

        if os.path.isdir(input_file):
            txt_files = get_txt_files_recursive(input_file)
            for txt_file in txt_files:
                basename = os.path.basename(txt_file)

                # Calculate index for this file
                if basename not in basename_indices:
                    basename_indices[basename] = 0
                basename_indices[basename] += 1

                # Build display name
                if basename_count[basename] > 1:
                    display_name = f"{txt_file}[{basename_indices[basename]}]"
                else:
                    display_name = txt_file

                result = process_file(txt_file, exec1, exec2, display_name)
                if result is not True:
                    has_output_mismatches = True
                    _, output1, output2 = result
                    save_mismatched_outputs(txt_file, output1, output2, exec1, exec2)
                    mismatched_files.append(txt_file)

        else:
            basename = os.path.basename(input_file)

            # Calculate index for this file
            if basename not in basename_indices:
                basename_indices[basename] = 0
            basename_indices[basename] += 1

            # Build display name
            if basename_count[basename] > 1:
                display_name = f"{input_file}[{basename_indices[basename]}]"
            else:
                display_name = input_file

            result = process_file(input_file, exec1, exec2, display_name)
            if result is not True:
                has_output_mismatches = True
                _, output1, output2 = result
                save_mismatched_outputs(input_file, output1, output2, exec1, exec2)
                mismatched_files.append(input_file)

    print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")

    if has_output_mismatches:
        print(f"{Fore.YELLOW}Results saved in results/ folder{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
        interactive_compare_loop(mismatched_files)
    else:
        print(f"{Fore.GREEN}All tests passed! No mismatches found.{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
