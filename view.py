import cv2
import numpy as np
import argparse

argparser = argparse.ArgumentParser(
    description="A script to parse and play back a raw video recording."
)
argparser.add_argument(
    "path",
    help="Path to the .raw file to parse and play back."
)
argparser.add_argument(
    "width",
    help="Footage width in pixels.",
    type=int
)
argparser.add_argument(
    "height",
    help="Footage height in pixels.",
    type=int
)
argparser.add_argument(
    "stride",
    help="Length of each image row in bytes.",
    type=int
)
argparser.add_argument(
    "density",
    help="Density of bits per pixel.",
    type=int
)
args = argparser.parse_args()
filepath = args.path
width = args.width
height = args.height
density = args.density

try:
    with open(filepath, 'r') as file:
        raw_data = file.read()
except FileNotFoundError:
    print("[ERR] Raw data file not found!")


