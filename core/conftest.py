"""
conftest.py — LASE core test configuration.
Ensures luminark/ and core/ are on sys.path for all builds.
"""
import sys, os
_core = os.path.dirname(os.path.abspath(__file__))
_lum  = os.path.join(_core, "luminark")
if _lum  not in sys.path: sys.path.insert(0, _lum)
if _core not in sys.path: sys.path.insert(0, _core)
