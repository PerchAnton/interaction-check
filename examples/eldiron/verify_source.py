"""Verify the pinned, unmodified Eldiron checkout before building the consumer."""
from pathlib import Path
import subprocess

SOURCE = Path(__file__).resolve().parents[2] / '.artifacts/eldiron-source'
PIN = 'c1ac529b501745a38d78f633ba23d2254c2ec71c'

def verify():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SOURCE, text=True).strip()
    if head != PIN:
        raise ValueError('unexpected Eldiron revision')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=SOURCE, text=True):
        raise ValueError('Eldiron source must be clean')
    print('Verified Eldiron source at', head)

if __name__ == '__main__':
    verify()
