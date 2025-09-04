#!/usr/bin/env python3
import json
import toml
import subprocess
import shutil
from pathlib import Path

def build_metadata(manifest_path='xai_components_manifest.jsonl',
                   output_index='index.json',
                   metadata_dir='metadata',
                   clone_root='.clones'):
    """
    1. Reads a JSONL manifest of component libraries.
    2. For each entry, clones its repo at the given ref into clone_root.
    3. Extracts [project] info from pyproject.toml, using null if missing (lists default to []).
    4. Merges manifest info + project info, writes per-library JSON.
    5. Builds an index.json of all metadata files.
    6. Cleans up clone directories.
    """
    meta_dir = Path(metadata_dir)
    meta_dir.mkdir(exist_ok=True)
    clone_dir = Path(clone_root)

    index = []
    with open(manifest_path, 'r', encoding='utf-8') as mf:
        for line in mf:
            entry = json.loads(line)
            lib_id = entry['library_id']
            repo_url = entry['url']
            ref      = entry.get('git_ref', 'main')
            target   = clone_dir / lib_id.lower()

            # 2) clone & checkout
            subprocess.run(['git', 'clone', repo_url, str(target)], check=True)

            # 3) load pyproject.toml if exists
            proj_data = {}
            xircuits_cfg = {}
            pyproj = target / 'pyproject.toml'
            if pyproj.exists():
                cfg = toml.load(pyproj)
                proj_data    = cfg.get('project', {})
                xircuits_cfg = (cfg.get('tool') or {}).get('xircuits', {})
            else:
                print(f"⚠️  {lib_id}: pyproject.toml not found, using nulls where missing")

            # default_example_path lives in [tool.xircuits]
            default_example_path = entry.get("default_example_path", xircuits_cfg.get("default_example_path"))

            metadata = {
                # manifest fields
                'library_id': lib_id,
                'path':       entry['path'],
                'url':        repo_url,
                'git_ref':    ref,
                # project fields
                'version':      proj_data.get("version"),
                'description':  proj_data.get("description"),
                'authors':      proj_data.get("authors", []),
                'license':      proj_data.get("license"),
                'readme':       proj_data.get("readme", None),
                'repository':   proj_data.get("repository", None),
                'keywords':     proj_data.get("keywords", []),
                'requirements': proj_data.get("dependencies", []),
                'default_example_path': default_example_path,
            }

            # write per-library JSON
            out_file = meta_dir / f"{lib_id.lower()}.json"
            with open(out_file, 'w', encoding='utf-8') as of:
                json.dump(metadata, of, indent=2)

            index.append({
                "library_id":           lib_id,
                "name":                 entry.get("name", proj_data.get("name")),
                "path":                 entry.get("path"),
                "metadata":             out_file.as_posix(),
                "version":              entry.get("version", metadata.get("version")),
                "description":          entry.get("description", metadata.get("description")),
                "authors":              entry.get("authors", metadata.get("authors")),
                "license":              entry.get("license", metadata.get("license")),
                "readme":               entry.get("readme", metadata.get("readme")),
                "repository":           entry.get("repository", metadata.get("repository")),
                "keywords":             entry.get("keywords", metadata.get("keywords")),
                "requirements":         entry.get("requirements", metadata.get("requirements")),
                "url":                  entry.get("url", metadata.get("url")),
                "git_ref":              entry.get("git_ref", metadata.get("git_ref")),
                "default_example_path": default_example_path,
            })


    # write index.json
    with open(output_index, 'w', encoding='utf-8') as idxf:
        json.dump(index, idxf, indent=2)

    # optionally remove clone_root entirely
    print(f"Generated {len(index)} metadata files in '{metadata_dir}' and wrote '{output_index}'")

if __name__ == '__main__':
    build_metadata()
