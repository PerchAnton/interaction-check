"""Install a candidate wheel in a clean environment and check jsonpatch 1.39."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("distribution", type=Path, help="directory containing exactly one wheel")
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    wheels = list(args.distribution.glob("*.whl"))
    if len(wheels) != 1:
        parser.error("expected exactly one candidate wheel")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheels[0].resolve()),
                        "jsonpatch==1.39", "jsonpointer==3.5"], check=True, cwd=root)
        subprocess.run([str(python), "-I", "-c",
                        "import pathlib, sys, interaction_check; "
                        "assert pathlib.Path(sys.prefix) in pathlib.Path(interaction_check.__file__).parents"],
                       check=True, cwd=root)
        subprocess.run([str(python), "-I", "-m", "unittest", "discover", "-s", str(HERE),
                        "-p", "native_tests.py"], check=True, cwd=root)
        command = [str(python), "-I", str(HERE / "verify.py"),
                   "--expected-version", args.expected_version]
        if args.report is not None:
            command += ["--report", str(args.report.resolve())]
        subprocess.run(command, check=True, cwd=root)


if __name__ == "__main__":
    main()
