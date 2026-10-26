"""Find Amp's native test executable and run its native control and replay adapter."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-log', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    binaries = []
    for line in args.build_log.read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        if item.get('reason') == 'compiler-artifact' and item.get('executable') and item.get('profile', {}).get('test'):
            binaries.append(item['executable'])
    if len(binaries) != 1:
        parser.error('expected one libtest executable')
    result = subprocess.run([binaries[0], '--exact', 'interaction_check_bridge::native_unicode_history'], cwd=args.source, timeout=60)
    if result.returncode:
        return result.returncode
    report = ROOT / '.artifacts/consumer-reports/amp.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run([sys.executable, str(ROOT / 'interaction_check.py'), '--timeout', '60', '--trace',
                           '--report', str(report), *map(str, sorted((HERE / 'scenarios').glob('*.json'))), '--',
                           sys.executable, str(HERE / 'adapter.py'), '--binary', binaries[0], '--source', str(args.source.resolve())], cwd=ROOT).returncode

if __name__ == '__main__':
    raise SystemExit(main())
