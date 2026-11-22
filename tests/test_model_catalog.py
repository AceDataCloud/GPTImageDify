import json
import shutil

import dify_plugin  # noqa: F401 - patch network before requests/SSL imports
import pytest
import yaml

from scripts.sync_model_catalog import CATALOG, ROOT, SOURCES, sync
from tools.acedata_client import AceDataGPTImageClient
from tools.api_contracts import ENDPOINTS

CATALOG_DATA = json.loads(CATALOG.read_text())


def test_every_published_model_reaches_dify_and_runtime_validation():
    assert not sync(CATALOG_DATA, check=True)
    for name, source in SOURCES.items():
        tool = yaml.safe_load((ROOT / source["tool"]).read_text())
        parameter = next(p for p in tool["parameters"] if p["name"] == "model")
        expected = CATALOG_DATA["models"][name]
        assert [item["value"] for item in parameter["options"]] == expected
        assert ENDPOINTS[name]["properties"]["model"]["enum"] == expected
        assert ENDPOINTS[name]["schema"]["properties"]["model"]["enum"] == expected
        assert parameter["default"] == "gpt-image-2"
        assert {"gpt-image-2.6-flare", "gpt-image-2.6-sunburst:reverse", "nano-banana-2.1"} <= set(
            expected
        )


@pytest.mark.parametrize(
    "name,model",
    [(name, model) for name, models in CATALOG_DATA["models"].items() for model in models],
)
def test_each_model_survives_real_request_preparation(name, model):
    inputs = {"prompt": "Offline schema check", "model": model}
    if name == "gpt_image_edit_image":
        inputs["image_urls"] = "https://example.org/owned-reference.png"
    method, path, body, _, _, readonly, _ = AceDataGPTImageClient("placeholder").prepare(
        name, inputs
    )
    assert method == "POST" and path == SOURCES[name]["path"]
    assert body["model"] == model and not readonly


def test_sync_refuses_to_silently_replace_a_retired_default(tmp_path):
    (tmp_path / "tools").mkdir()
    for source in SOURCES.values():
        shutil.copyfile(ROOT / source["tool"], tmp_path / source["tool"])
    catalog = json.loads(CATALOG.read_text())
    catalog["models"]["gpt_image_generate_image"].remove("gpt-image-2")
    with pytest.raises(ValueError, match="do not replace it automatically"):
        sync(catalog, root=tmp_path)
