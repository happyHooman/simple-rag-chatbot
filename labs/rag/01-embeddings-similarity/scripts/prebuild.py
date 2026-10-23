#!/usr/bin/env python3
"""Prebuild script to run sanity checks before deployment."""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False


def main():
    """Run all prebuild checks."""
    print("🚀 Running prebuild sanity checks...")
    print("=" * 50)
    
    checks = [
        (["ruff", "check", "app/"], "Code linting"),
        (["mypy", "app/"], "Type checking"),
        (["pytest", "tests/sanity/", "--live", "-v"], "Sanity tests"),
    ]
    
    all_passed = True
    
    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All prebuild checks passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("💥 Some prebuild checks failed. Fix issues before deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
