"""Replay an already built Rust consumer binary, without invoking Cargo per step."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('example', choices=['floem', 'helix', 'microsoft-edit', 'xilem'])
    parser.add_argument('--target-dir', type=Path, default=ROOT / '.artifacts/rust-consumers')
    args = parser.parse_args()
    executable = args.target_dir.resolve() / 'debug' / ('pilot-' + args.example + ('.exe' if sys.platform == 'win32' else ''))
    scenarios = sorted((ROOT / 'examples/rust-consumers' / args.example / 'scenarios').glob('*.json'))
    if not executable.is_file() or not scenarios:
        parser.error('build the consumer and provide its target directory first')
    report = ROOT / '.artifacts/consumer-reports' / (args.example + '.json')
    report.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run([sys.executable, str(ROOT / 'interaction_check.py'), '--timeout', '30', '--trace',
                           '--report', str(report), *map(str, scenarios), '--', str(executable)], cwd=ROOT).returncode

if __name__ == '__main__':
    raise SystemExit(main())
