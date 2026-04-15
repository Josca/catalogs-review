#!/usr/bin/env python3
"""Generate the Helm chart providers HTML report from YAML data files."""

import os
import sys
from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "providers"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"


def load_providers():
    """Load all provider YAML files and return a list of provider dicts."""
    providers = []
    for yaml_file in sorted(DATA_DIR.glob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        providers.append(data)
    return providers


def compute_overlap(providers):
    """Build a dict of chart_name -> {category, providers: [short_names]}."""
    overlap = {}
    for p in providers:
        short = p["provider"]["short_name"]
        for chart in p.get("charts", []):
            name = chart["name"]
            if name not in overlap:
                overlap[name] = {"category": chart["category"], "providers": []}
            if short not in overlap[name]["providers"]:
                overlap[name]["providers"].append(short)
    return overlap


def compute_stats(providers, overlap):
    """Compute summary statistics."""
    total_charts = sum(len(p.get("charts", [])) for p in providers)
    unique_charts = len(overlap)
    categories = sorted({chart["category"] for p in providers for chart in p.get("charts", [])})
    return total_charts, unique_charts, categories


def main():
    if not DATA_DIR.exists():
        print(f"Error: data directory not found: {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    providers = load_providers()
    if not providers:
        print("Error: no provider YAML files found", file=sys.stderr)
        sys.exit(1)

    overlap = compute_overlap(providers)
    total_charts, unique_charts, categories = compute_stats(providers, overlap)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
    template = env.get_template("report.html.j2")

    html = template.render(
        providers=providers,
        overlap=overlap,
        total_charts=total_charts,
        unique_charts=unique_charts,
        categories=categories,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "report.html"
    output_file.write_text(html)
    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    main()
