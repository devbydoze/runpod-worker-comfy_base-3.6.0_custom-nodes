import numpy as np
import torch

class MostSimilarColorDetector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "target_color": ("STRING", {"default": "#FF0000"}),  # Default: Red
                "threshold": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.5,
                    "display": "slider"
                }),
            },
        }

    RETURN_TYPES = (
        "INT", "INT", "INT",  # Bright RGB
        "INT", "INT", "INT",  # Mid RGB (most similar)
        "INT", "INT", "INT",  # Dark RGB
        "STRING", "STRING", "STRING"  # Hex color codes
    )
    RETURN_NAMES = (
        "R_bright", "G_bright", "B_bright",
        "R_mid", "G_mid", "B_mid",
        "R_dark", "G_dark", "B_dark",
        "Bright_Color_Hex", "Mid_Color_Hex", "Dark_Color_Hex"
    )

    FUNCTION = "detect_similar_color"

    CATEGORY = "Color Detection"

    def hex_to_rgb(self, hex_color):
        """ Convert hex color (e.g., #FF5733) to RGB tuple (255, 87, 51). """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def detect_similar_color(self, image, target_color, threshold):
        """ Detects the most similar color in the image based on a given hex color. """
        
        # Convert target hex color to RGB
        target_rgb = np.array(self.hex_to_rgb(target_color)) / 255.0  # Normalize to [0, 1]

        # Convert image tensor to numpy array for processing
        img_np = image.cpu().numpy()[0]  # Assuming batch size 1
        img_np = np.clip(img_np, 0, 1)  # Clamp values between 0 and 1 for valid RGB

        # Extract RGB channels
        red_channel = img_np[:, :, 0]
        green_channel = img_np[:, :, 1]
        blue_channel = img_np[:, :, 2]

        # Calculate Euclidean distance between each pixel and target color
        color_distance = np.sqrt(
            (red_channel - target_rgb[0]) ** 2 +
            (green_channel - target_rgb[1]) ** 2 +
            (blue_channel - target_rgb[2]) ** 2
        )

        # Find the closest color match
        min_distance = np.min(color_distance)
        closest_match_mask = color_distance == min_distance

        if closest_match_mask.sum() == 0:  # Fallback in case no close match is found
            closest_match_mask = color_distance <= np.percentile(color_distance, 1)  # Use the top 1% closest

        # Calculate the most similar (mid) color
        mid_r = int(np.mean(red_channel[closest_match_mask]) * 255)
        mid_g = int(np.mean(green_channel[closest_match_mask]) * 255)
        mid_b = int(np.mean(blue_channel[closest_match_mask]) * 255)

        # Generate brighter and darker versions based on threshold
        bright_r = min(255, mid_r + int(threshold * (255 - mid_r) / 10))
        bright_g = min(255, mid_g + int(threshold * (255 - mid_g) / 10))
        bright_b = min(255, mid_b + int(threshold * (255 - mid_b) / 10))

        dark_r = max(0, mid_r - int(threshold * mid_r / 10))
        dark_g = max(0, mid_g - int(threshold * mid_g / 10))
        dark_b = max(0, mid_b - int(threshold * mid_b / 10))

        # Convert RGB values to hex for display purposes
        bright_color_hex = f"#{bright_r:02X}{bright_g:02X}{bright_b:02X}"
        mid_color_hex = f"#{mid_r:02X}{mid_g:02X}{mid_b:02X}"
        dark_color_hex = f"#{dark_r:02X}{dark_g:02X}{dark_b:02X}"

        return (
            bright_r, bright_g, bright_b,
            mid_r, mid_g, mid_b,
            dark_r, dark_g, dark_b,
            bright_color_hex, mid_color_hex, dark_color_hex
        )

# Register the node
NODE_CLASS_MAPPINGS = {
    "MostSimilarColorDetector": MostSimilarColorDetector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MostSimilarColorDetector": "Most Similar Color Detector"
}
