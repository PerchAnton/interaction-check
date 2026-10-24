# PhotoCraft Session adapter

An external integration pilot combining three independent projects:

- `edit-session` from `PerchAnton/edit-session`, revision `28620b8264660ea84a182110cf5894da90281c42`.
- `photocraft-doc` and `photocraft-engine` from `storytold/photocraft`, revision
  `14a4ab9b3f38f0b68fde6add97384919710374c8`.
- The JSONL scenario runner in this repository.

All Rust dependencies are resolved in `Cargo.lock`. The adapter has no local path dependency.
The library does not depend on PhotoCraft or on the scenario runner.

The fixture is a synthetic 8×8 document with two ordinary raster layers above a Background.
`begin` captures document ID, target layer ID and PhotoCraft's revision. `preview` changes
only the parameter draft. `commit` checks that context and calls the engine's
`layer.setProps` command once if the final value differs. Cancel and no-op commits make no
engine call. External changes, target switches, Undo and Redo go through `Session` too.
The adapter never records or restores snapshots itself.

Run from the repository root with Rust 1.99+ (tested on 1.99.1) and Python 3.10+:

```sh
cargo build --locked --manifest-path adapters/photocraft/Cargo.toml
python3 interaction_check.py scenarios/photocraft/*.json -- \
  adapters/photocraft/target/debug/edit-session-photocraft-probe
```

The first build includes PhotoCraft's engine and its dependencies and can take several minutes.
JSONL input and replies follow the runner's protocol; each scenario gets a fresh engine Session.
No personal files, installed PhotoCraft instance, GUI connection or credentials are needed.

This demonstrates host integration through real command dispatch. It does not modify
PhotoCraft's shipped UI, implement a selection preview, solve a particular upstream issue,
or establish that maintainers will accept an external dependency. Rendering, persistence,
other depths and modes, selection masks and a PdfCraft adapter are still outside this pilot.
