#!/usr/bin/env python3
"""
Convenience wrapper for the setup verification script.
Run from project root: python verify.py
"""

if __name__ == "__main__":
    from src.backend.verify_setup import main
    import sys
    sys.exit(main())


