"""Add the external bridge only to a clean, disposable checkout at the pinned revision."""
import argparse
from pathlib import Path
import shutil
import subprocess

PIN = 'df97a3c01e6021a464af4204dd64d10eb205f149'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def prepare(source):
    source = source.resolve()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    if head != PIN:
        raise ValueError('wrong Amp revision')
    dirty = subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True)
    if dirty:
        raise ValueError('Amp checkout must be clean; do not overwrite local work')
    manifest = source / 'Cargo.toml'
    text = manifest.read_text(encoding='utf-8')
    if text.count('[dev-dependencies]') != 1:
        raise ValueError('unexpected manifest')
    protocol = (ROOT / 'examples/rust-consumers/protocol').as_posix()
    text = text.replace('[dev-dependencies]', '[dev-dependencies]\nserde_json = "1"\npilot-protocol = { path = "' + protocol + '" }')
    text += '\n[workspace]\n\n[profile.dev]\ndebug = 0\nincremental = false\n'
    manifest.write_text(text, encoding='utf-8')
    lib = source / 'src/lib.rs'
    lib.write_text(lib.read_text(encoding='utf-8') + '\n#[cfg(test)]\nmod interaction_check_bridge;\n', encoding='utf-8')
    shutil.copyfile(HERE / 'bridge.rs', source / 'src/interaction_check_bridge.rs')
    lock = HERE / 'Cargo.lock'
    if lock.is_file():
        shutil.copyfile(lock, source / 'Cargo.lock')
    print('Prepared disposable Amp checkout at', head)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    prepare(parser.parse_args().source)
