#!/usr/bin/env python3
"""
Validation script to check code structure before installing dependencies.
Run this to verify the codebase is ready to use.
"""

import ast
import sys
from pathlib import Path


def validate_python_syntax(file_path: Path) -> tuple[bool, str]:
    """Validate Python file syntax.

    Args:
        file_path: Path to Python file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def main():
    """Run validation checks."""
    print("🔍 NBA Predictor - Code Validation")
    print("=" * 60)

    src_dir = Path("src/nba_predictor")
    if not src_dir.exists():
        print("❌ src/nba_predictor directory not found!")
        print("   Make sure you're running this from the project root.")
        sys.exit(1)

    print("\n📝 Checking Python syntax...")

    python_files = list(src_dir.rglob("*.py"))
    errors = []

    for py_file in sorted(python_files):
        rel_path = py_file
        is_valid, error = validate_python_syntax(py_file)

        if is_valid:
            print(f"  ✓ {rel_path}")
        else:
            print(f"  ✗ {rel_path}")
            print(f"    Error: {error}")
            errors.append((rel_path, error))

    print("\n" + "=" * 60)

    if errors:
        print(f"\n❌ Found {len(errors)} file(s) with errors:")
        for path, error in errors:
            print(f"\n  {path}:")
            print(f"    {error}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(python_files)} Python files validated successfully!")
        print("\n📦 Next steps:")
        print("  1. Create virtual environment: python3 -m venv venv")
        print("  2. Activate it: source venv/bin/activate")
        print("  3. Install dependencies: pip install -r requirements.txt")
        print("  4. Configure environment: cp .env.example .env")
        print("  5. Initialize database: python -m nba_predictor.cli init")
        print("\n🏀 Ready to start predicting NBA games!")
        sys.exit(0)


if __name__ == "__main__":
    main()
