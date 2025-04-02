import numpy as np
import torch

class MostGreenElementDetector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
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
        "INT", "INT", "INT",  # Mid RGB (purest green)
        "INT", "INT", "INT",  # Dark RGB
        "STRING", "STRING", "STRING"  # Hex color codes
    )
    RETURN_NAMES = (
        "R_bright", "G_bright", "B_bright",
        "R_mid", "G_mid", "B_mid",
        "R_dark", "G_dark", "B_dark",
        "Bright_Color_Hex", "Mid_Color_Hex", "Dark_Color_Hex"
    )

    FUNCTION = "detect_green"

    CATEGORY = "Color Detection"

    def detect_green(self, image, threshold):
        # Convert image tensor to numpy array for processing
        img_np = image.cpu().numpy()[0]  # Assuming batch size 1
        img_np = np.clip(img_np, 0, 1)  # Clamp values between 0 and 1 for valid RGB

        # Extract RGB channels
        red_channel = img_np[:, :, 0]
        green_channel = img_np[:, :, 1]
        blue_channel = img_np[:, :, 2]

        # Calculate "greenness" score (maximize green while minimizing red and blue)
        greenness = green_channel - (red_channel + blue_channel) / 2
        greenness_norm = (greenness - greenness.min()) / (greenness.max() - greenness.min())

        # Create mask for purest green
        mid_mask = greenness_norm >= 0.99
        if mid_mask.sum() == 0:
            mid_mask = greenness_norm >= greenness_norm.max()

        # Calculate mid RGB values (purest green)
        mid_r, mid_g, mid_b = np.mean(red_channel[mid_mask]), np.mean(green_channel[mid_mask]), np.mean(blue_channel[mid_mask])
        mid_r, mid_g, mid_b = int(mid_r * 255), int(mid_g * 255), int(mid_b * 255)

        # Ensure mid green tone is at the core and bright and dark tones adjust from it
        # Calculate bright and dark based on threshold
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

NODE_CLASS_MAPPINGS = {
    "MostGreenElementDetector": MostGreenElementDetector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MostGreenElementDetector": "Most Green Element Detector",
}
