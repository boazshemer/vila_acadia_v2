#!/usr/bin/env python3
"""
Convenience script to run tests with common configurations.
Run from project root: python run_tests.py
"""
import sys
import subprocess


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    """Run tests with different configurations."""
    print("\n🧪 Vila Acadia Test Suite Runner\n")
    
    # Check if pytest is installed
    check = subprocess.run(
        "python -m pytest --version",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if check.returncode != 0:
        print("❌ pytest is not installed!")
        print("\nInstall test dependencies:")
        print("  pip install pytest pytest-cov pytest-mock httpx\n")
        return 1
    
    print(f"✓ pytest version: {check.stdout.strip()}\n")
    
    # Ask user what to run
    print("Select test mode:")
    print("  1. Run all tests (fast)")
    print("  2. Run all tests with coverage")
    print("  3. Run specific test file")
    print("  4. Run tests matching pattern")
    print("  5. Run with verbose output")
    print("  6. Run and generate HTML coverage report")
    
    try:
        choice = input("\nEnter choice (1-6, or press Enter for option 2): ").strip() or "2"
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled by user.")
        return 1
    
    if choice == "1":
        return run_command("pytest", "Running all tests")
    
    elif choice == "2":
        return run_command(
            "pytest --cov=src/backend --cov-report=term",
            "Running all tests with coverage"
        )
    
    elif choice == "3":
        print("\nAvailable test files:")
        print("  - tests/test_api_endpoints.py")
        print("  - tests/test_gsheets_service.py")
        print("  - tests/test_models.py")
        print("  - tests/test_config.py")
        
        try:
            file_name = input("\nEnter test file name: ").strip()
            if not file_name.startswith("tests/"):
                file_name = f"tests/{file_name}"
            if not file_name.endswith(".py"):
                file_name = f"{file_name}.py"
            
            return run_command(f"pytest {file_name} -v", f"Running {file_name}")
        except (KeyboardInterrupt, EOFError):
            print("\n\nCancelled by user.")
            return 1
    
    elif choice == "4":
        try:
            pattern = input("\nEnter test pattern (e.g., 'test_auth'): ").strip()
            return run_command(f"pytest -k {pattern} -v", f"Running tests matching '{pattern}'")
        except (KeyboardInterrupt, EOFError):
            print("\n\nCancelled by user.")
            return 1
    
    elif choice == "5":
        return run_command("pytest -vv", "Running all tests (verbose)")
    
    elif choice == "6":
        result = run_command(
            "pytest --cov=src/backend --cov-report=html --cov-report=term",
            "Running tests with HTML coverage report"
        )
        if result == 0:
            print("\n✓ HTML coverage report generated in: htmlcov/index.html")
            print("  Open it in your browser to view detailed coverage.\n")
        return result
    
    else:
        print(f"\n❌ Invalid choice: {choice}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test run cancelled by user.")
        sys.exit(1)

