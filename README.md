# xai-components-manifest

A centralized repository for managing metadata of Xircuits remote component libraries. This manifest enables Xircuits to dynamically discover, configure, and install remote component libraries without requiring a full release of Xircuits.

---

## Repository Structure

```
├── xai_components_manifest.jsonl   # JSONL manifest of all remote component libraries
├── create_metadata.py             # Script to generate per-library metadata
├── index.json                     # Auto-generated; lists all metadata files
└── metadata/                      # Auto-generated; one JSON file per library
    ├── xai_pycaret.json
    ├── xai_modelstash.json
    └── ...
```

---

## Prerequisites

- Python 3.9+
- `git` installed and on your `PATH`
- Python packages (install via `pip`):
  ```bash
  pip install toml
  ```

---

## 1. Adding a New Component Library

Add a new entry to the manifest file `xai_components_manifest.jsonl`. You can do this via the command line or a text editor.

### Command Line Example

```bash
echo '{"path": "xai_components/xai_twilio", "url": "https://github.com/XpressAI/xai-twilio", "library_id": "TWILIO", "git_ref": "main"}' \
  >> xai_components_manifest.jsonl
```

### Text Editor Example

Open `xai_components_manifest.jsonl` in your preferred editor and append a new line:

```jsonl
{"path": "xai_components/xai_twilio", "url": "https://github.com/XpressAI/xai-twilio", "library_id": "TWILIO", "git_ref": "main"}
```

---

## 2. Generating Metadata

Run the `create_metadata.py` script. This will:

1. Clone each repository listed in `xai_components_manifest.jsonl`.
2. Extract relevant fields from each library’s `pyproject.toml` (from `[project]` and `tool.xircuits`).
3. Fill missing values with defaults (`"N/A"` or empty lists).
4. Produce an `index.json` and a `metadata/` folder containing one JSON file per library.

```bash
python create_metadata.py
```

After running, you’ll see:

- **index.json**: An array of objects, each with:

  - `library_id`
  - `path`
  - `metadata` (relative path to the per-library JSON file)

- **metadata/\<library\_id>.json**: For each component library, a JSON file with fields:

  - **Manifest data**: `path`, `url`, `library_id`, `git_ref`
  - **Project data**: `version`, `description`, `authors`, `license`, `readme`, `repository`, `keywords`, `requirements`
  - 
---

## 3. Integration into Xircuits

Xircuits clones and reads `index.json` at startup to locate each library’s metadata. It uses this information to:

1. Build the `component_library_config.json`
2. Clone and install remote component libraries as needed

Keep this manifest up to date whenever adding, removing, or updating a remote component library.

---

## Future Work

- Add CI checks to ensure `index.json` and `metadata/` files are in sync.
- Implement a static site generator to render library metadata automatically.
- Support versioning or tagging beyond a simple `git_ref`.

---

