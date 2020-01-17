#!/usr/bin/env python3
import sys
import os
print(''.join(os.fsencode(a).decode() for a in sys.argv[1:]))

