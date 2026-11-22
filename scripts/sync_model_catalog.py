"""Keep Dify's image selectors and runtime validation on the published API enums."""

import argparse
import json
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "tools/model_catalog.json"
SOURCES = {
    "gpt_image_generate_image": {
        "url": "https://platform.acedata.cloud/api/v1/apis/8f01fe72-8a3e-4872-8d8d-330cde179b3a/",
        "path": "/openai/images/generations",
        "tool": "tools/gpt_image_generate.yaml",
    },
    "gpt_image_edit_image": {
        "url": "https://platform.acedata.cloud/api/v1/apis/fb74083e-bb68-48d5-8ba6-b5a224400cd3/",
        "path": "/openai/images/edits",
        "tool": "tools/gpt_image_edit.yaml",
    },
}


def fetch() -> dict:
    models = {}
    for name, source in SOURCES.items():
        response = requests.get(source["url"], timeout=(10, 30), allow_redirects=False)
        response.raise_for_status()
        api = response.json()
        operation = api["definition"]["paths"][source["path"]]["post"]
        model_schema = operation["requestBody"]["content"]["application/json"]["schema"][
            "properties"
        ]["model"]
        ids = model_schema["enum"]
        if not ids or not all(isinstance(value, str) and value for value in ids):
            raise ValueError(f"Invalid published model enum for {name}")
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate model enum for {name}")
        models[name] = ids
    return {"sources": SOURCES, "models": models}


def sync(catalog: dict, root: Path = ROOT, check: bool = False) -> list[str]:
    files = {"tools/model_catalog.json": json.dumps(catalog, indent=2) + "\n"}
    for name, source in SOURCES.items():
        path = root / source["tool"]
        tool = yaml.safe_load(path.read_text())
        parameter = next(item for item in tool["parameters"] if item["name"] == "model")
        existing = {item["value"]: item for item in parameter["options"]}
        ids = catalog["models"][name]
        if parameter.get("default") not in ids:
            raise ValueError(
                f"Review the retired default model in {name}; do not replace it automatically"
            )
        parameter["options"] = [
            existing.get(value, {"value": value, "label": {"en_US": value, "zh_Hans": value}})
            for value in ids
        ]
        files[source["tool"]] = yaml.safe_dump(tool, sort_keys=False, allow_unicode=True)
    changed = []
    for relative, expected in files.items():
        path = root / relative
        if path.exists() and path.read_text() == expected:
            continue
        changed.append(relative)
        if not check:
            path.write_text(expected)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = fetch() if args.refresh else json.loads(CATALOG.read_text())
    changed = sync(catalog, check=args.check)
    print(f"Model counts: { {key: len(value) for key, value in catalog['models'].items()} }")
    if args.check and changed:
        raise SystemExit("Regenerate model selectors: " + ", ".join(changed))


if __name__ == "__main__":
    main()
