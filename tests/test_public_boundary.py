from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def test_repository_does_not_contain_real_env_file() -> None:
    assert not list(ROOT.rglob(".env"))


def test_readme_has_explicit_proprietary_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "production strategy, proprietary parameters" in readme.lower()
    assert "intentionally excluded" in readme.lower()


def test_demo_images_are_generic_and_have_no_text_metadata() -> None:
    images = [path for path in (ROOT / "docs" / "assets").glob("*.png")]
    assert images
    for path in images:
        assert path.name.startswith(("demo_", "synthetic_"))
        with Image.open(path) as image:
            assert "Software" not in image.info
            assert "Creation Time" not in image.info
