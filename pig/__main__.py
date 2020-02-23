"""
Command line wrapper
"""
import os
import sys
from __init__ import main
if sys.path[0] != os.getcwd():
    sys.path.insert(0, os.getcwd())
main()


