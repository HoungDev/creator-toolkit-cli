# README demo

The animated README demo is generated from the current Creator Toolkit source. It calls the same
CLI entry logic shown to users, creates two non-sensitive sample image files in a temporary
directory, and removes that directory when rendering finishes.

## Rebuild the asset

From the repository root:

```bash
python -m pip install -e ".[demo]"
python scripts/render_readme_demo.py
```

The renderer writes `docs/assets/creator-toolkit-demo.gif`. Title and tag examples pass a fixed
`--seed` so reviews get a stable visual diff; suggestions still vary between runs when the option
is omitted.

## Demo transcript

```console
$ creator-toolkit title "creator workflow" --seed 2026
10 Creator Workflow Tips Every Beginner Should Know

$ creator-toolkit tags --count 3 --seed 2026
automation
productivity
tutorial

$ creator-toolkit rename demo-images --prefix campaign --dry-run
Planned 2 image(s).
cover.jpg -> campaign_1.jpg
thumbnail.png -> campaign_2.png
```

The final command is a preview. It does not change either sample filename.
