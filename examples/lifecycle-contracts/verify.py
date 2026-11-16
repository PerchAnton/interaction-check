"""Check installed runner traces, retaining the known Contra mismatch as a failure."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def verify(output):
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for library in ['mitt', 'typed-signals', 'emittery', 'contra']:
        for scenario in ['write-emit-unsubscribe', 'unknown-unsubscribe']:
            report = output / f'{library}-{scenario}.json'
            run = subprocess.run([sys.executable, '-m', 'interaction_check', '--trace', '--report', str(report.resolve()),
                str(HERE / 'scenarios' / f'{scenario}.json'), '--', 'node', str(HERE / 'adapter.mjs'), library],
                capture_output=True, text=True, encoding='utf-8', timeout=30, cwd=HERE)
            known = library == 'contra' and scenario == 'unknown-unsubscribe'
            if run.returncode != (1 if known else 0):
                raise AssertionError(run.stdout + run.stderr)
            data = json.loads(report.read_text())
            if known:
                row = data['results'][0]['trace'][-1]
                assert row['step'] == 5 and any('state.callbacks' in d for d in row['differences']), row
            results.append({'library': library, 'scenario': scenario, 'exit_code': run.returncode,
                'known_mismatch': known, 'report': report.name, 'sha256': hashlib.sha256(report.read_bytes()).hexdigest()})
    record = {'schema': 1, 'interaction-check': importlib.metadata.version('interaction-check'),
        'scope': 'Application lifecycle observations; not upstream adoption, timing, or complete emitter equivalence',
        'packages': json.loads((HERE / 'package-lock.json').read_text())['packages']['']['dependencies'],
        'results': results}
    (output / 'index.json').write_text(json.dumps(record, indent=2)+'\n')
    print('8 traces retained: 7 pass, 1 expected Contra failure at step 5, state.callbacks.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    verify(parser.parse_args().output)
