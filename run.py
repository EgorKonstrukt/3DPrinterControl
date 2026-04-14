#!/usr/bin/env python3

import sys
import os

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

import main

if __name__ == '__main__':
    sys.exit(main.main())

