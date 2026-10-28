"""Forward protocol messages to Amp's real command code in its native test harness."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python_protocol import serve

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    process = subprocess.Popen([str(args.binary.resolve()), '--exact', 'interaction_check_bridge::replay',
                                '--ignored', '--nocapture', '--format', 'terse'], cwd=args.source,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr)
    counter = 0
    def step(event):
        nonlocal counter
        counter += 1
        packet = {'protocol': 1, 'id': counter, 'event': event}
        process.stdin.write(json.dumps(packet, ensure_ascii=False).encode('utf-8') + b'\n')
        process.stdin.flush()
        # libtest adds a bounded startup banner. Native JSON output is written directly,
        # not through println!, so it is never swallowed by libtest's capture facility.
        for _ in range(8):
            line = process.stdout.readline(65537)
            if not line or len(line) > 65536:
                raise ValueError('Amp bridge exited or exceeded response limit')
            if line.strip() in (b'', b'running 1 test'):
                continue
            reply = json.loads(line)
            if set(reply) != {'protocol', 'id', 'state'} or reply['protocol'] != 1 or reply['id'] != counter:
                raise ValueError('unexpected Amp response')
            return reply['state']
        raise ValueError('Amp startup output exceeded limit')
    try:
        serve(step)
        process.stdin.close()
        if process.wait(timeout=10):
            raise ValueError('Amp native test bridge failed')
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

if __name__ == '__main__':
    main()
