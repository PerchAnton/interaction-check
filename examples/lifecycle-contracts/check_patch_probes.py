"""Assert precise native baseline observations and optional exact-source fixes."""
import argparse
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent

def check(output, fixed):
    output.mkdir(parents=True, exist_ok=True)
    for library, folder in [('rfc6902', fixed.rfc6902), ('jsondiffpatch', fixed.jsondiffpatch), ('fast-json-patch', fixed.fast_json_patch)]:
        for label, source in [('published', None)] + ([('fixed', folder)] if folder else []):
            run = subprocess.run(['node', str(HERE / 'patch_probe.mjs'), library] + ([str(source.resolve())] if source else []),
                capture_output=True, text=True, timeout=30, check=True)
            data = json.loads(run.stdout)
            (output / f'{library}-{label}.json').write_text(run.stdout)
            rows = data['results']
            if library == 'rfc6902':
                assert len(rows) == 9
                assert all(r['rejected'] == bool(source) and r['unchanged'] == bool(source) for r in rows), rows
            elif library == 'jsondiffpatch':
                assert len(rows) == 2
                assert all(r['unchanged'] == bool(source) for r in rows), rows
                if source: assert all(r['error'] is None for r in rows), rows
                else: assert all("doesn't support text diffs" in r['error'] for r in rows), rows
            else:
                assert len(rows) == 4
                assert all(r['replacement'] == {'ok': True} for r in rows), rows
                if source:
                    assert all(r['error']['name'] == 'OPERATION_PATH_CANNOT_ADD' for r in rows), rows
                else:
                    # The published CommonJS build is non-strict: 0/false/"" are silently ignored.
                    assert all(r['error'] is None for r in rows[:3]), rows
                    assert rows[3]['error']['name'] == 'TypeError', rows
            print(library, label, 'observations verified')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rfc6902', type=Path)
    p.add_argument('--jsondiffpatch', type=Path)
    p.add_argument('--fast-json-patch', type=Path)
    a = p.parse_args()
    check(a.output, a)
