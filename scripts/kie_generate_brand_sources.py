#!/usr/bin/env python3
"""Generate text-free Sosa Tech visual sources through kie.ai.

The script intentionally reads KIE_API_KEY only from the process environment.
It stores prompts and task metadata next to the downloaded image but never
stores or prints the credential.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
STATUS_URL = "https://api.kie.ai/api/v1/jobs/recordInfo?taskId={}"

PROMPT_CORE = (
    "Premium editorial technology illustration for a bilingual Miami "
    "small-business technology consultancy. Carbon-black background "
    "#080A0F, restrained electric-teal #00E5C8 signal paths, graphite "
    "#131820 panels, subtle technical grid, clean negative space, realistic "
    "depth, precise modern lighting, one clear focal point, practical business "
    "technology rather than science fiction, no typography, no letters, no "
    "numbers, no logos, no watermark."
)

SCENES = {
    "connected-lead-flow": (
        "A visual journey beginning with one incoming customer inquiry on the "
        "left, flowing through three clean connected system nodes, and arriving "
        "at a clear completed follow-up state on the right. Use abstract cards "
        "and signal paths only; no recognizable app interfaces. Leave generous "
        "dark negative space in the upper third for a headline overlay."
    ),
    "automation-routing": (
        "A precise automation routing scene: one customer message enters, then "
        "branches into contact update, team notification, scheduled action, and "
        "visible status. Represent it as elegant abstract nodes and panels, not "
        "a real application. Leave negative space on the left for copy."
    ),
    "reliable-infrastructure": (
        "A calm reliable infrastructure scene with a primary server node, an "
        "encrypted off-site backup path, a monitoring signal, and a verified "
        "recovery loop. Sophisticated and reassuring, not a data-center stock "
        "photo. Leave negative space in the upper-left for copy."
    ),
}


def request_json(url: str, api_key: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SosaTechBrandProduction/1.0",
        },
        method="GET" if payload is None else "POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"kie.ai HTTP {exc.code}: {detail[:500]}") from exc


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "SosaTechBrandProduction/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        destination.write_bytes(response.read())


def generate(name: str, scene: str, output_dir: Path, api_key: str) -> dict:
    prompt = f"{PROMPT_CORE} {scene}"
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "4:5",
            "output_format": "png",
        },
    }
    created = request_json(CREATE_URL, api_key, payload)
    task_id = ((created.get("data") or {}).get("taskId"))
    if not task_id:
        raise RuntimeError(f"kie.ai did not return a task ID for {name}")
    print(f"created {name}: task {task_id}", flush=True)

    deadline = time.monotonic() + 12 * 60
    record: dict = {}
    while time.monotonic() < deadline:
        time.sleep(15)
        record = request_json(STATUS_URL.format(task_id), api_key)
        data = record.get("data") or {}
        state = data.get("state")
        print(f"{name}: {state}", flush=True)
        if state == "fail":
            raise RuntimeError(f"kie.ai task failed for {name}")
        if state == "success":
            try:
                result_urls = json.loads(data.get("resultJson") or "{}").get(
                    "resultUrls", []
                )
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid result JSON for {name}") from exc
            if not result_urls:
                raise RuntimeError(f"kie.ai returned no image URL for {name}")
            extension = ".png"
            image_path = output_dir / f"{name}{extension}"
            download(result_urls[0], image_path)
            metadata = {
                "name": name,
                "task_id": task_id,
                "model": payload["model"],
                "aspect_ratio": payload["input"]["aspect_ratio"],
                "prompt": prompt,
                "source_url": result_urls[0],
                "output": image_path.name,
            }
            (output_dir / f"{name}.json").write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
            return metadata
    raise TimeoutError(f"kie.ai timed out for {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--scene",
        action="append",
        choices=sorted(SCENES),
        help="Generate only selected scenes; defaults to all.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("KIE_API_KEY", "").strip()
    if not api_key:
        print("KIE_API_KEY is required", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = args.scene or list(SCENES)
    manifest = []
    for name in selected:
        manifest.append(generate(name, SCENES[name], output_dir, api_key))
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"generated {len(manifest)} source images in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
