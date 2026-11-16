"""Keep the published jsondiff crash and verify the proposed upstream fix separately."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fixed-jsondiff', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
before = subprocess.run(['go', 'test', '-count=1', '-v'], cwd=HERE, capture_output=True, text=True, timeout=120)
(args.output / 'jsondiff-before.log').write_text(before.stdout + before.stderr)
if before.returncode == 0 or 'slice bounds out of range' not in before.stdout or 'jsondiff.findKey' not in before.stdout:
    raise AssertionError('Expected the pinned v0.7.1 Rationalize regression; see raw log')
with tempfile.TemporaryDirectory(prefix='patch-fixed-') as directory:
    target = Path(directory)
    for name in ['main.go', 'main_test.go', 'go.mod', 'go.sum']:
        shutil.copyfile(HERE / name, target / name)
    with (target / 'go.mod').open('a') as file:
        file.write(f'\nreplace github.com/wI2L/jsondiff => {args.fixed_jsondiff.resolve()}\n')
    after = subprocess.run(['go', 'test', '-count=1', '-v'], cwd=target, capture_output=True, text=True, timeout=120)
    (args.output / 'jsondiff-after.log').write_text(after.stdout + after.stderr)
    if after.returncode != 0:
        raise AssertionError('The fixed source did not pass; see raw log')
(args.output / 'fix-comparison.json').write_text(json.dumps({
    'published': {'version': '0.7.1', 'exit_code': before.returncode, 'result': 'panic reproduced'},
    'candidate': {'commit': '93a94633a7ee0afa1434c29c4e86f1f1b00fb589', 'exit_code': after.returncode, 'result': 'native tests passed'},
    'scope': 'Small native before/after corpus, not the upstream full suite or a released fix'
}, indent=2) + '\n')
