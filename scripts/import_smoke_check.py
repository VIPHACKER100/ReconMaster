import importlib.util
import traceback
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
print(f"Repo root: {ROOT}")

# Collect top-level python files to check
files = [p for p in ROOT.glob('*.py')]
# Optionally include other candidate modules
candidates = [p for p in files if p.name not in ('scripts',)]

failures = []

def smoke_check():
    for p in sorted(candidates):
        module_name = p.stem
        print(f"\n--- Importing: {p.name} as module '{module_name}' ---")
        
        # Mock sys.argv to prevent argparse from exiting if it finds unknown args
        original_argv = sys.argv
        sys.argv = [str(p), "--help"]
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(p))
            mod = importlib.util.module_from_spec(spec)
            
            # Ensure module executes with the repo root on sys.path
            sys.path.insert(0, str(ROOT))
            
            try:
                spec.loader.exec_module(mod)
                print(f"OK: {p.name}")
            except SystemExit:
                # SystemExit is often called by argparse --help or similar
                print(f"OK (SystemExit): {p.name}")
            
        except Exception:
            print(f"FAILED: {p.name}")
            traceback.print_exc()
            failures.append((p.name, traceback.format_exc()))
        finally:
            sys.argv = original_argv
            # remove repo root from sys.path if present at index 0
            try:
                if sys.path[0] == str(ROOT):
                    sys.path.pop(0)
            except Exception:
                pass

print('\n=== Summary ===')
if failures:
    print(f"{len(failures)} module(s) failed to import:")
    for name, tb in failures:
        print(f"- {name}")
    sys.exit(2)
else:
    print("All imports OK")
    sys.exit(0)
