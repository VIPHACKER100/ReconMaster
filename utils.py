import subprocess
import os
import sys
import glob
import shlex
import shutil
from typing import List, Optional


def safe_run(cmd, timeout: Optional[int] = None):
    """Run a command safely without shell=True when possible.

    cmd can be a list (preferred) or a string. Returns (stdout, stderr, returncode).
    """
    # Add local bin to PATH for the current process
    local_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    env = os.environ.copy()
    if os.path.exists(local_bin):
        env["PATH"] = local_bin + os.pathsep + env.get("PATH", "")

    # Resolve full path of the command
    if isinstance(cmd, list):
        exe = cmd[0]
        full_path = shutil.which(exe, path=env["PATH"])
        if full_path:
            cmd[0] = full_path
        cmd_list = [str(c) for c in cmd]
    else:
        # String command
        try:
            parts = shlex.split(cmd)
            if parts:
                exe = parts[0]
                full_path = shutil.which(exe, path=env["PATH"])
                if full_path:
                    parts[0] = full_path
                cmd_list = parts
            else:
                cmd_list = []
        except Exception:
            # Fallback for complex strings
            return _run_in_shell(cmd, timeout, env)

    try:
        proc = subprocess.run(
            cmd_list, shell=False, capture_output=True, text=True, timeout=timeout, env=env
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timeout after {timeout}s", 1
    except FileNotFoundError as e:
        # Final fallback to shell if which missed something
        return _run_in_shell(cmd, timeout, env)
    except Exception as e:
        return "", str(e), 1

def _run_in_shell(cmd, timeout, env):
    """Helper for shell=True fallback"""
    import subprocess
    if isinstance(cmd, list):
        cmd = " ".join([f'"{c}"' if " " in c else c for c in cmd])
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timeout after {timeout}s", 1
    except Exception as e:
        return "", str(e), 1


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
