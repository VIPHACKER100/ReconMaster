import subprocess
import os
import sys
import glob
import shlex
import shutil
from typing import List, Optional


def safe_run(cmd, timeout: Optional[int] = None, env: Optional[dict] = None):
    """Run a command safely with robust group-level timeout termination.

    cmd can be a list (preferred) or a string. Returns (stdout, stderr, returncode).
    """
    local_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    if env is None:
        env = os.environ.copy()
    else:
        # Merge passed env with system env for PATH consistency
        base_env = os.environ.copy()
        base_env.update(env)
        env = base_env

    if os.path.exists(local_bin):
        env["PATH"] = local_bin + os.pathsep + env.get("PATH", "")

    if isinstance(cmd, list):
        exe = cmd[0]
        full_path = shutil.which(exe, path=env["PATH"])
        if full_path:
            cmd[0] = full_path
        cmd_list = [str(c) for c in cmd]
    else:
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
            return _run_in_shell(cmd, timeout, env)

    return _execute_with_timeout(cmd_list, False, timeout, env)

def _run_in_shell(cmd, timeout, env):
    """Helper for shell=True fallback with timeout termination"""
    if isinstance(cmd, list):
        cmd = " ".join([f'"{c}"' if " " in c else c for c in cmd])
    return _execute_with_timeout(cmd, True, timeout, env)

def _execute_with_timeout(cmd, shell, timeout, env):
    """Execute a command and ensure it and all children are killed on timeout"""
    import subprocess
    import signal
    import time

    # Start the process with a different session/process group if on Unix
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "env": env,
        "shell": shell
    }
    
    if sys.platform != "win32":
        kwargs["preexec_fn"] = os.setsid

    try:
        proc = subprocess.Popen(cmd, **kwargs)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return stdout, stderr, proc.returncode
        except subprocess.TimeoutExpired:
            if sys.platform == "win32":
                # On Windows, taskkill /T /F is more reliable for trees
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], 
                             capture_output=True, check=False)
            else:
                # On Unix, kill the entire process group
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            
            stdout, stderr = proc.communicate() # Clean up
            return stdout, stderr if stderr else f"Timeout after {timeout}s", 1
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
