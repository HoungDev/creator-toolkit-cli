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

The renderer writes `docs/assets/creator-toolkit-demo.gif`. Title and tag examples use a fixed
seed in the renderer so reviews get a stable visual diff; normal CLI suggestions still vary
between runs.

## Demo transcript

```console
$ creator-toolkit title "creator workflow"
10 Creator Workflow Tips Every Beginner Should Know

$ creator-toolkit tags --count 3
automation
productivity
tutorial

$ creator-toolkit rename demo-images --dry-run
Planned 2 image(s).
cover.jpg -> image_1.jpg
thumbnail.png -> image_2.png
```

The final command is a preview. It does not change either sample filename.
