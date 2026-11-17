"""Keep raw passing and failed reports; optionally compare exact upstream fixes."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def verify(output, pubsub_fixed=None, automat_source=None):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    cases = [('tiny-unknown-off', ['node', str(HERE / 'adapter.mjs')], None),
             ('atom-rebinding', [sys.executable, str(HERE / 'controllers.py'), 'atom'], None),
             ('atom-replacement-notification', [sys.executable, str(HERE / 'controllers.py'), 'atom'], 2),
             ('traits-readonly-notification', [sys.executable, str(HERE / 'controllers.py'), 'traits'], 1)]
    for name, adapter, failure in cases:
        report = output / (name + '.json')
        run = subprocess.run([sys.executable, '-m', 'interaction_check', '--trace', '--report', str(report.resolve()),
                              str(HERE / 'scenarios' / (name + '.json')), '--', *adapter],
                             capture_output=True, text=True, encoding='utf-8', timeout=30, cwd=HERE)
        assert run.returncode == (1 if failure else 0), run.stdout + run.stderr
        data = json.loads(report.read_text())
        if failure:
            row = data['results'][0]['trace'][-1]
            assert row['step'] == failure and any('state.callbacks' in x for x in row['differences']), row
        records.append({'scenario': name, 'exit_code': run.returncode, 'first_mismatch': failure,
                        'report': report.name, 'sha256': hashlib.sha256(report.read_bytes()).hexdigest()})

    js = """import { topicProbe } from './events.mjs';
const rows = [];
for (const method of ['clearSubscriptions', 'unsubscribe']) for (const parent of [true, false])
  rows.push(topicProbe(method, parent, process.argv[1]));
console.log(JSON.stringify(rows));"""
    for mode, path in [('published', None), ('fixed', pubsub_fixed)]:
        if mode == 'fixed' and path is None:
            continue
        args = ['node', '--input-type=module', '-e', js] + ([str(path.resolve())] if path else [])
        data = json.loads(subprocess.check_output(args, cwd=HERE, text=True, timeout=30))
        assert len(data) == 4
        for row in data:
            assert row['callbacks'] == ([['entering', 7]] if path else []), row
        (output / ('pubsub-' + mode + '.json')).write_text(json.dumps(data, indent=2) + '\n')

    for mode, source in [('published', None), ('fixed', automat_source)]:
        if mode == 'fixed' and source is None:
            continue
        env = os.environ.copy()
        # Avoid an inherited source override changing the published baseline.
        env.pop('PYTHONPATH', None)
        if source:
            env['PYTHONPATH'] = str(source.resolve())
        command = [sys.executable, str(HERE / 'automat_probe.py')] + (['--fixed'] if source else [])
        rows = json.loads(subprocess.check_output(command, cwd=HERE, env=env, text=True, timeout=30))
        assert rows[0]['read'] == 'LOADED' and rows[0]['read_error'] is None
        for row in rows[1:3]:
            assert row['factory_error'] in ['ValueError', 'FactoryAbort'] and row['read_error'] == 'AssertionError'
        if source:
            for row in rows[3:]:
                assert row['read'] == 'error' and row['read_error'] is None
                assert row['recovery'] == 'recovered' and row['after_recovery'] == 'idle'
        (output / ('automat-' + mode + '.json')).write_text(json.dumps(rows, indent=2) + '\n')
    record = {'schema': 1, 'scope': 'Bounded consumer checks, not upstream full suites or acceptance of a new dependency',
              'versions': {x: importlib.metadata.version(x) for x in ['interaction-check', 'atom', 'traits', 'automat']},
              'reports': records, 'pubsub_fixed_checked': pubsub_fixed is not None,
              'automat_fixed_checked': automat_source is not None}
    (output / 'index.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Four traces retained: two pass; two explicitly fail on callback expectations.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pubsub-fixed', type=Path, help='Exact PR #232 src/pubsub.js saved as a CommonJS .cjs file')
    parser.add_argument('--automat-source', type=Path, help='Exact PR #177 src directory; does not install or replace the baseline')
    args = parser.parse_args()
    verify(args.output, args.pubsub_fixed, args.automat_source)
