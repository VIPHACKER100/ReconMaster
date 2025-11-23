import subprocess
import os
import glob
import shlex
from typing import List, Optional


def safe_run(cmd, timeout: Optional[int] = None):
    """Run a command safely without shell=True when possible.

    cmd can be a list (preferred) or a string. Returns (stdout, stderr, returncode).
    """
    # If a string is provided, attempt to split into args and run without a shell.
    if isinstance(cmd, str):
        try:
            parts = shlex.split(cmd)
            if parts:
                proc = subprocess.run(
                    parts, shell=False, capture_output=True, text=True, timeout=timeout
                )
                return proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired:
            return "", f"Timeout after {timeout}s", 1
        except FileNotFoundError as e:
            return "", str(e), 127
        except Exception:
            # As a last resort (if parsing fails), fall back to shell=True but keep it explicit
            try:
                proc = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=timeout
                )
                return proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired:
                return "", f"Timeout after {timeout}s", 1
            except FileNotFoundError as e:
                return "", str(e), 127

    # Ensure all parts are strings for list input
    cmd_list = [str(c) for c in cmd]
    try:
        proc = subprocess.run(
            cmd_list, shell=False, capture_output=True, text=True, timeout=timeout
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timeout after {timeout}s", 1
    except FileNotFoundError as e:
        return "", str(e), 127


def merge_and_dedupe_text_files(input_dir: str, pattern: str, output_file: str):
    """Merge all text files matching pattern (relative to input_dir) into output_file, unique sorted lines.

    pattern should be a glob pattern like "*.txt" or "*.json". This avoids shell-only utilities.
    """
    paths = glob.glob(os.path.join(input_dir, pattern))
    lines = set()
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        lines.add(line)
        except FileNotFoundError:
            continue

    sorted_lines = sorted(lines)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        for line in sorted_lines:
            out.write(line + "\n")


def find_wordlist(preferred_paths: List[str]) -> Optional[str]:
    """Return the first existing path from preferred_paths or None."""
    for p in preferred_paths:
        if os.path.exists(p):
            return p
    return None
