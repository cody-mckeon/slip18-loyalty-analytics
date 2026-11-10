"""Build an offline-ready executive dashboard from committed synthetic JSON results."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "email": ROOT / "results/prospective_email/experiment_report.json",
    "design": ROOT / "results/prospective_email/frozen_design.json",
    "personalization": ROOT / "results/offer_optimization/evaluation_report.json",
    "policy": ROOT / "results/offer_optimization/frozen_policy.json",
}


def build(out: Path | None = None) -> Path:
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in SOURCES.items()}
    assert data["email"]["checks"]["passed"] is True, "Email integrity checks failed"
    assert data["email"]["groups"]["0"]["assigned"] + data["email"]["groups"]["1"]["assigned"] == data["email"]["checks"]["total"]
    assert data["personalization"]["policy"] == data["policy"]["policy"]
    template = (ROOT / "dashboard_template.html").read_text(encoding="utf-8")
    raw_json = json.dumps(data, sort_keys=True, separators=(",", ":")).replace("<", "\\u003c")
    html = template.replace("/*__EMBEDDED_DATA__*/", "const DATA = " + raw_json + ";")
    if "/*__EMBEDDED_DATA__*/" in html:
        raise RuntimeError("Dashboard data injection failed")
    destination = out or (ROOT / "dashboard.html")
    destination.write_text(html, encoding="utf-8")
    return destination


if __name__ == "__main__":
    output = build()
    print(f"Built {output} ({output.stat().st_size:,} bytes) using committed synthetic result JSON")