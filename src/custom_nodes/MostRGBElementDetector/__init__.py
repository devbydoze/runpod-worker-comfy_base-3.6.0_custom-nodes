from .most_red_element_detector import MostRedElementDetector
from .most_green_element_detector import MostGreenElementDetector
from .most_blue_element_detector import MostBlueElementDetector
from .most_orange_element_detector import MostOrangeElementDetector
from .most_yellow_element_detector import MostYellowElementDetector
from .most_grey_element_detector import MostGreyElementDetector
from .hex_color_detector import MostSimilarColorDetector

NODE_CLASS_MAPPINGS = {
    "MostRedElementDetector": MostRedElementDetector,
    "MostGreenElementDetector": MostGreenElementDetector,
    "MostBlueElementDetector": MostBlueElementDetector,
    "MostOrangeElementDetector": MostOrangeElementDetector,
    "MostYellowElementDetector": MostYellowElementDetector,
    "MostGreyElementDetector": MostGreyElementDetector,
    "MostSimilarColorDetector": MostSimilarColorDetector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MostRedElementDetector": "Most Red Element Detector",
    "MostGreenElementDetector": "Most Green Element Detector",
    "MostBlueElementDetector": "Most Blue Element Detector",
    "MostOrangeElementDetector": "Most Orange Element Detector",
    "MostYellowElementDetector": "Most Yellow Element Detector",
    "MostGreyElementDetector": "Most Grey Element Detector",
    "MostSimilarColorDetector": "Hex Color Detector",
}
