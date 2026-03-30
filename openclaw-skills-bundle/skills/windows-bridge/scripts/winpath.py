#!/usr/bin/env python3
import sys, re

def wsl_to_windows(path: str) -> str:
    m = re.match(r'^/mnt/([a-zA-Z])/(.*)$', path)
    if not m:
        return path
    drive = m.group(1).upper()
    rest = m.group(2).replace('/', '\\')
    return f'{drive}:\\{rest}'

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(wsl_to_windows(p))
