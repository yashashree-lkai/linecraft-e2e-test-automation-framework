"""
utils/visual_helper.py — Pixel-diff based visual regression testing.

Workflow:
1. First run  → baseline images are saved automatically (no diff).
2. Later runs → new screenshots are diffed against baseline.
3. On failure → a side-by-side diff image is saved to screenshots/.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageChops, ImageDraw

if TYPE_CHECKING:
    from playwright.sync_api import Page

BASELINE_DIR = Path("screenshots/baseline")
ACTUAL_DIR = Path("screenshots/actual")
DIFF_DIR = Path("screenshots/diff")

for _d in (BASELINE_DIR, ACTUAL_DIR, DIFF_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Max allowed proportion of differing pixels (0-1). Override via env.
DEFAULT_THRESHOLD: float = float(os.getenv("VISUAL_THRESHOLD", "0.2"))


def capture_and_compare(
    page: "Page",
    name: str,
    selector: str | None = None,
    threshold: float = DEFAULT_THRESHOLD,
    update_baseline: bool = False,
) -> None:
    """
    Take a screenshot and compare it to the stored baseline.

    Args:
        page:             Playwright Page object.
        name:             Unique identifier for this screenshot (no extension).
        selector:         CSS selector to screenshot a specific element.
                          If None, the full page is captured.
        threshold:        Max fraction of pixels allowed to differ (0–1).
        update_baseline:  If True, overwrite the baseline and skip comparison.
                          Useful for intentional UI changes.

    Raises:
        AssertionError: if the pixel difference exceeds the threshold.
    """
    baseline_path = BASELINE_DIR / f"{name}.png"
    actual_path = ACTUAL_DIR / f"{name}.png"
    diff_path = DIFF_DIR / f"{name}_diff.png"

    # Take screenshot
    if selector:
        locator = page.locator(selector)
        locator.screenshot(path=str(actual_path))
    else:
        page.screenshot(path=str(actual_path), full_page=True)

    # First run — save as baseline
    if not baseline_path.exists() or update_baseline:
        import shutil
        shutil.copy(actual_path, baseline_path)
        print(f"[visual] Baseline saved: {baseline_path}")
        return

    # Compare
    baseline_img = Image.open(baseline_path).convert("RGB")
    actual_img = Image.open(actual_path).convert("RGB")

    # Resize if dimensions changed (avoids crash; still flags as different)
    if baseline_img.size != actual_img.size:
        actual_img = actual_img.resize(baseline_img.size, Image.LANCZOS)

    diff_img = ImageChops.difference(baseline_img, actual_img)
    pixels = list(diff_img.getdata())
    total = len(pixels)
    differing = sum(1 for p in pixels if any(c > 10 for c in p))  # ignore tiny noise
    ratio = differing / total

    if ratio > 0:
        _save_diff_composite(baseline_img, actual_img, diff_img, diff_path)

    assert ratio <= threshold, (
        f"[visual] '{name}' differs by {ratio:.2%} "
        f"(threshold {threshold:.2%}). "
        f"Diff saved to {diff_path}"
    )
    print(f"[visual] '{name}' passed — {ratio:.2%} pixels differ.")


def _save_diff_composite(
    baseline: Image.Image,
    actual: Image.Image,
    diff: Image.Image,
    out_path: Path,
) -> None:
    """Save a 3-panel composite: baseline | actual | diff (amplified)."""
    w, h = baseline.size
    composite = Image.new("RGB", (w * 3 + 20, h), color=(30, 30, 30))
    composite.paste(baseline, (0, 0))
    composite.paste(actual, (w + 10, 0))

    # Amplify diff channel so subtle changes are visible
    amplified = diff.point(lambda x: min(x * 8, 255))
    composite.paste(amplified, (w * 2 + 20, 0))

    draw = ImageDraw.Draw(composite)
    draw.text((5, 5), "BASELINE", fill=(255, 255, 100))
    draw.text((w + 15, 5), "ACTUAL", fill=(255, 255, 100))
    draw.text((w * 2 + 25, 5), "DIFF (×8)", fill=(255, 100, 100))

    composite.save(str(out_path))


def update_all_baselines(page: "Page", screenshots: list[tuple[str, str | None]]) -> None:
    """
    Helper to regenerate multiple baselines in one call.

    Args:
        screenshots: list of (name, selector_or_None) tuples.
    """
    for name, selector in screenshots:
        capture_and_compare(page, name, selector=selector, update_baseline=True)
