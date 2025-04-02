# MostRedElementDetector Node

This custom node for ComfyUI detects the "most red" areas in an input image and outputs three sets of RGB values, based on a threshold slider for sensitivity.

## Installation
Place this folder in the `C:\StabilityMatrix\Data\Packages\ComfyUI\custom_nodes` directory.

## Usage
1. Open ComfyUI.
2. Find the node under "Color Detection" as "Most Red Element Detector."
3. Connect an image input and adjust the `threshold` slider.
4. Use the RGB outputs in `Color to Mask` nodes or other image processing nodes.

## Parameters
- **threshold**: A slider (0-10) to adjust sensitivity for red detection.
