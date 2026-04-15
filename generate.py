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
        resolve_chart_urls(data)
        providers.append(data)
    return providers


def resolve_chart_urls(data):
    """Set chart URLs from per-chart url field or provider chart_url_template."""
    template = data["provider"].get("chart_url_template")
    for chart in data.get("charts", []):
        if chart.get("url"):
            continue
        if template:
            chart["url"] = template.format(name=chart["name"])
        else:
            chart["url"] = ""


def compute_overlap(providers):
    """Build a dict of app_name -> {category, providers: [short_names]}.

    Charts with an 'app' field are grouped under that canonical name;
    otherwise the chart 'name' is used as the key.
    """
    overlap = {}
    for p in providers:
        short = p["provider"]["short_name"]
        for chart in p.get("charts", []):
            app = chart.get("app", chart["name"])
            if app not in overlap:
                overlap[app] = {"category": chart["category"], "providers": []}
            if short not in overlap[app]["providers"]:
                overlap[app]["providers"].append(short)
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
    output_file = OUTPUT_DIR / "index.html"
    output_file.write_text(html)
    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    main()
