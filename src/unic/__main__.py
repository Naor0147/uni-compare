import argparse
import os
import platform
import subprocess
import sys
import shlex  # Used to split command strings into args
import re     # Used for parsing Valgrind output
from pathlib import Path

from colorama import Fore, Style, init
from pyfiglet import Figlet

# Initialize colorama
init(autoreset=True)

parser = argparse.ArgumentParser(
    description="A simple program to help university students manage their coursework. Given 2 executable files, it will run them and compare their outputs with the given input file/s."
)

parser.add_argument("exec1", help="Path to the first executable file (can include args in quotes, e.g. './prog 10').")
parser.add_argument("exec2", help="Path to the second executable file (can include args in quotes).")
parser.add_argument(
    "--files",
    "-f",
    nargs="+",
    help="List of input files to test the executables with.",
    required=True,
)
parser.add_argument(
    "--max-depth",
    "-d",
    type=int,
    default=5,
    help="Maximum directory depth for recursive search (default: 5)",
)
parser.add_argument(
    "--output",
    "-o",
    type=str,
    default="uniTestResults",
    help="Directory to save results (default: uniTestResults)",
)
parser.add_argument(
    "--valgrind",
    "-v",
    action="store_true",
    help="Run executables with Valgrind to check for memory leaks/errors.",
)
parser.add_argument(
    "--timeout",
    "-t",
    type=float,
    default=5.0,
    help="Timeout in seconds for each test execution (default: 5.0)",
)

def get_safe_results_path(input_file, base_output_dir):
    """
    Generates a safe relative path for saving results to avoid [Errno 17].
    Converts absolute paths to relative structure.
    """
    # Normalize path and handle drive letters
    abs_path = os.path.abspath(input_file)
    drive, path_no_drive = os.path.splitdrive(abs_path)
    
    # Remove leading separator to ensure os.path.join treats it as relative
    rel_path = path_no_drive.lstrip(os.sep)
    
    # If there was a drive letter (Windows), add it as a folder
    if drive:
        rel_path = os.path.join(drive.replace(":", ""), rel_path)
        
    return os.path.join(base_output_dir, rel_path)

def check_valgrind_errors(stderr_output):
    """
    Parses Valgrind stderr output to determine if there were memory errors.
    Returns True if errors/leaks were found.
    """
    if not stderr_output:
        return False
    
    # Look for the error summary line
    # Example: "ERROR SUMMARY: 0 errors from 0 contexts"
    match = re.search(r"ERROR SUMMARY: (\d+) errors", stderr_output)
    if match:
        error_count = int(match.group(1))
        if error_count > 0:
            return True
            
    # Also check for "definitely lost" bytes just in case
    if "definitely lost: 0 bytes" not in stderr_output and "definitely lost:" in stderr_output:
         return True
         
    return False

def process_file(input_file, exec1_cmd, exec2_cmd, display_name=None, use_valgrind=False, timeout=5.0):
    """
    Runs both programs with the given input file and compares their output.
    Also runs Valgrind if requested.
    """
    
    # Parse the command strings into executable and arguments
    try:
        exec1_parts = shlex.split(exec1_cmd)
        exec2_parts = shlex.split(exec2_cmd)
    except Exception as e:
        print(f"{Fore.RED}Error parsing command arguments: {e}{Style.RESET_ALL}")
        return False, None

    # Get absolute paths for the executables
    exec1_path = os.path.abspath(exec1_parts[0])
    exec2_path = os.path.abspath(exec2_parts[0])

    # Construct the final command lists
    cmd1 = [exec1_path] + exec1_parts[1:]
    cmd2 = [exec2_path] + exec2_parts[1:]

    # Add Valgrind wrapper if requested
    if use_valgrind:
        # --leak-check=full: detailed leak report
        # --quiet: suppress verbose text (only show errors)
        valgrind_prefix = ["valgrind", "--leak-check=full", "--quiet"]
        cmd1 = valgrind_prefix + cmd1
        cmd2 = valgrind_prefix + cmd2

    display_text = display_name if display_name else input_file

    # Read input file
    try:
        with open(input_file, "r") as f:
            input_data = f.read()
    except IOError as e:
        print(
            f"{Fore.RED}Error reading input file {display_text}: {e}{Style.RESET_ALL}"
        )
        return False, None

    # Run executables
    try:
        proc1 = subprocess.Popen(
            cmd1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            output1, stderr1 = proc1.communicate(input=input_data, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc1.kill()
            print(f"{Fore.YELLOW}[T] {display_text} (Timeout){Style.RESET_ALL}")
            return False, None

        proc2 = subprocess.Popen(
            cmd2,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            output2, stderr2 = proc2.communicate(input=input_data, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc2.kill()
            print(f"{Fore.YELLOW}[T] {display_text} (Timeout){Style.RESET_ALL}")
            return False, None

    except FileNotFoundError:
        if use_valgrind:
             print(f"{Fore.RED}Error: 'valgrind' not found. Please install it or remove the --valgrind flag.{Style.RESET_ALL}")
        else:
             print(f"{Fore.RED}Error running executables. Check paths.{Style.RESET_ALL}")
        return False, None
    except Exception as e:
        print(f"{Fore.RED}Error running executables: {e}{Style.RESET_ALL}")
        return False, None

    # Result Data Structure
    result_data = {
        "output1": output1,
        "output2": output2,
        "stderr1": stderr1 if use_valgrind else None,
        "stderr2": stderr2 if use_valgrind else None,
        "valgrind_error1": check_valgrind_errors(stderr1) if use_valgrind else False,
        "valgrind_error2": check_valgrind_errors(stderr2) if use_valgrind else False
    }

    # Logic for Success/Failure
    
    # 1. Output Mismatch
    if output1 != output2:
        print(f"{Fore.RED}[✗] {display_text} (Output Mismatch){Style.RESET_ALL}")
        return False, result_data

    # 2. Valgrind Memory Errors (only if enabled)
    if use_valgrind:
        if result_data["valgrind_error1"] or result_data["valgrind_error2"]:
            print(f"{Fore.MAGENTA}[M] {display_text} (Memory Error){Style.RESET_ALL}")
            if result_data["valgrind_error1"]:
                 print(f"    {Fore.MAGENTA}↳ Memory leaks in Exec 1{Style.RESET_ALL}")
            if result_data["valgrind_error2"]:
                 print(f"    {Fore.MAGENTA}↳ Memory leaks in Exec 2{Style.RESET_ALL}")
            return False, result_data

    # 3. Success
    print(f"{Fore.GREEN}[✓] {display_text}{Style.RESET_ALL}")
    return True, result_data


def save_mismatched_outputs(input_file, result_data, exec1_cmd, exec2_cmd, base_output_dir):
    """Save outputs (and Valgrind logs) for failed tests."""
    try:
        results_dir = get_safe_results_path(input_file, base_output_dir)
        Path(results_dir).mkdir(parents=True, exist_ok=True)

        def clean_filename(cmd_str):
            name = os.path.basename(cmd_str)
            name = name.replace(".exe", "")
            return "".join(c if c.isalnum() or c in " .-_" else "_" for c in name)

        exec1_name = clean_filename(exec1_cmd)
        exec2_name = clean_filename(exec2_cmd)

        # Save Standard Outputs
        with open(os.path.join(results_dir, f"{exec1_name}_output.txt"), "w") as f:
            f.write(result_data["output1"])

        with open(os.path.join(results_dir, f"{exec2_name}_output.txt"), "w") as f:
            f.write(result_data["output2"])

        # Save Valgrind Logs if they exist
        if result_data["stderr1"]:
            with open(os.path.join(results_dir, f"{exec1_name}_valgrind.txt"), "w") as f:
                f.write(result_data["stderr1"])
        
        if result_data["stderr2"]:
            with open(os.path.join(results_dir, f"{exec2_name}_valgrind.txt"), "w") as f:
                f.write(result_data["stderr2"])

    except IOError as e:
        print(f"{Fore.RED}Error saving results for {input_file}: {e}{Style.RESET_ALL}")


def handle_windows_beyond_compare():
    """Handle Beyond Compare setup for Windows."""
    default_path = r"C:\Program Files\Beyond Compare 4\bcomp.exe"

    if os.path.exists(default_path):
        print(f"{Fore.GREEN}Found Beyond Compare at default location.{Style.RESET_ALL}")
        os.environ["PATH"] += f";{os.path.dirname(default_path)}"
        return True
    else:
        print(f"{Fore.YELLOW}Beyond Compare not found at default location.{Style.RESET_ALL}")
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

    # Find the two output files (ending in _output.txt)
    try:
        for file in os.listdir(results_dir):
            if file.endswith("_output.txt"):
                if exec1_file is None:
                    exec1_file = os.path.join(results_dir, file)
                else:
                    exec2_file = os.path.join(results_dir, file)
                    break
    except FileNotFoundError:
         print(f"{Fore.RED}Error: Results directory not found: {results_dir}{Style.RESET_ALL}")
         return

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

        if platform.system() == "Windows":
            setup_success = handle_windows_beyond_compare()
        else:
            setup_success = handle_linux_beyond_compare()

        if setup_success:
            try:
                subprocess.Popen(cmd)
            except FileNotFoundError:
                print(f"{Fore.RED}Failed to open Beyond Compare.{Style.RESET_ALL}")
                sys.exit(1)
        else:
            print(f"{Fore.RED}Failed to set up Beyond Compare.{Style.RESET_ALL}")
            sys.exit(1)


def get_txt_files_recursive(directory, max_depth=5):
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


def interactive_compare_loop(mismatched_files, base_output_dir):
    """Interactive loop to view mismatches in Beyond Compare."""
    basename_count = {}
    file_mapping = {}

    for full_path in mismatched_files:
        basename = os.path.basename(full_path)
        if basename not in basename_count:
            basename_count[basename] = 0
        basename_count[basename] += 1

    basename_seen = {}
    for full_path in mismatched_files:
        basename = os.path.basename(full_path)
        
        # Use the same safe path logic for retrieval
        results_path = get_safe_results_path(full_path, base_output_dir)

        if basename_count[basename] > 1:
            if basename not in basename_seen:
                basename_seen[basename] = 0
            basename_seen[basename] += 1
            display_name = f"{basename}[{basename_seen[basename]}]"
        else:
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
                continue

            if user_input not in file_mapping:
                print(f"{Fore.RED}Error: '{user_input}' not found.{Style.RESET_ALL}")
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
    max_depth = args.max_depth
    output_dir = args.output
    use_valgrind = args.valgrind
    timeout = args.timeout

    has_output_mismatches = False
    mismatched_files = []

    fig = Figlet(font="slant")
    banner = fig.renderText("UniCompare")
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{banner}{Style.RESET_ALL}")

    description = "A simple program to help university students manage their coursework.\nGiven 2 executable files, it will run them and compare their outputs with the given input file/s."
    print(f"{Fore.YELLOW}{description}{Style.RESET_ALL}")
    
    if use_valgrind:
        print(f"{Fore.MAGENTA}Memory Check Mode (Valgrind) Enabled{Style.RESET_ALL}")
    
    print(f"{Fore.MAGENTA}Author: Denis Irkl (6'1 180lbs lean){Style.RESET_ALL}\n")

    print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
    print(
        f"{Style.BRIGHT}Running tests on {len(input_files)} file(s)...{Style.RESET_ALL}"
    )
    print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}\n")

    all_files = []
    basename_count = {}

    for input_file in input_files:
        if not os.path.exists(input_file):
            continue

        if os.path.isdir(input_file):
            txt_files = get_txt_files_recursive(input_file, max_depth)
            all_files.extend(txt_files)
        else:
            all_files.append(input_file)

    for file_path in all_files:
        basename = os.path.basename(file_path)
        basename_count[basename] = basename_count.get(basename, 0) + 1

    basename_indices = {}

    for input_file in input_files:
        if not os.path.exists(input_file):
            print(
                f"{Fore.RED}[✗] {input_file} (FILE/DIRECTORY NOT FOUND){Style.RESET_ALL}"
            )
            continue

        files_to_process = []
        if os.path.isdir(input_file):
            files_to_process = get_txt_files_recursive(input_file, max_depth)
        else:
            files_to_process = [input_file]

        for file_path in files_to_process:
            basename = os.path.basename(file_path)
            
            if basename not in basename_indices:
                basename_indices[basename] = 0
            basename_indices[basename] += 1

            if basename_count[basename] > 1:
                display_name = f"{file_path}[{basename_indices[basename]}]"
            else:
                display_name = file_path

            success, result_data = process_file(file_path, exec1, exec2, display_name, use_valgrind, timeout)
            
            if not success:
                if result_data is not None:
                    has_output_mismatches = True
                    save_mismatched_outputs(file_path, result_data, exec1, exec2, output_dir)
                    mismatched_files.append(file_path)

    print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")

    if has_output_mismatches:
        print(f"{Fore.YELLOW}Results saved in {output_dir}/ folder{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
        interactive_compare_loop(mismatched_files, output_dir)
    else:
        print(f"{Fore.GREEN}All tests passed! No mismatches found.{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()