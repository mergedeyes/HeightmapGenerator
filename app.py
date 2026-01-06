# This is a script to download heightmap tiles and generate a heightmap image.
# Creator: Jan Motulla - DE
# Date: 2026-01-06
# VERSION: 0.1

import os
import boto3 as aws
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError
import argparse
import math
import rasterio
import numpy as np
from PIL import Image

# Default paths, names and urls
TIF_LOCATION = "data/tif/"
HEIGHTMAP_LOCATION = "data/heightmaps/"
TILELIST_FILE = "data/tileList.txt"
S3_BUCKET_BASE = "copernicus-dem-30m"
DEFAULT_NORTHING = "N47_00"
DEFAULT_EASTING = "E009_00"
BASE_DIR_1 = "Copernicus_DSM_COG_10"
BASE_DIR_2 = "DEM"

# Ensure directories exist
os.makedirs(TIF_LOCATION, exist_ok=True)
os.makedirs(HEIGHTMAP_LOCATION, exist_ok=True)
os.makedirs(os.path.dirname(TILELIST_FILE) or ".", exist_ok=True)

# Define AWS client
s3 = aws.client("s3", config=Config(signature_version=UNSIGNED))

def parse_args():
    parser = argparse.ArgumentParser(
        description="Download Copernicus DEM tile"
    )

    parser.add_argument(
        "--northing",
        required=False,
        default=DEFAULT_NORTHING,
        help="Northing tile, e.g. N47_00"
    )
    parser.add_argument(
        "--easting",
        required=False,
        default=DEFAULT_EASTING,
        help="Easting tile, e.g. E009_00"
    )
    parser.add_argument(
        "--lat", 
        type=float,
        required=False,
        help="Latitude, e.g. 47.18"
        )
    parser.add_argument(
        "--lon", 
        type=float,
        required=False,
        help="Longitude, e.g. 9.42"
        )

    return parser.parse_args()

def CHECK_FILE(path: str) -> bool:
    return os.path.isfile(path) and os.path.getsize(path) > 0

# Define Download Functionality
def DOWNLOAD_FILE(OBJECT_NAME: str, FILE_NAME: str):
    if CHECK_FILE(FILE_NAME):
        print(f"File {FILE_NAME} already exists.")
        return True
    
    try:
        with open(FILE_NAME, "wb") as f:
            s3.download_fileobj(S3_BUCKET_BASE, OBJECT_NAME, f)
        print(f"File {FILE_NAME} successfully downloaded.")
    except ClientError:
        # Delete file if download fails
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        raise
    return CHECK_FILE(FILE_NAME)

def LOAD_TILELIST() -> set[str]:
    with open(TILELIST_FILE, "r") as f:
        return {line.strip() for line in f}

def TILE_AVAILABLE(tile_name: str) -> bool:
    return tile_name in TILES

def DOWNLOAD_TILE(NORTHING:str, EASTING:str):
    # Define file and path names
    S3_BASE_STR=f"{BASE_DIR_1}_{NORTHING}_{EASTING}_{BASE_DIR_2}"
    S3_FILE_PATH=f"{S3_BASE_STR}/{S3_BASE_STR}.tif"

    LOCAL_FILE_NAME=f"{NORTHING}_{EASTING}.tif"
    LOCAL_FILE_PATH = os.path.join(TIF_LOCATION, LOCAL_FILE_NAME)

    print("S3 key:", S3_FILE_PATH)
    print("Local file path:", LOCAL_FILE_PATH)
    if not TILE_AVAILABLE(S3_BASE_STR):
        print("Tile not available in tileList:", S3_BASE_STR)
        return None
    ok = DOWNLOAD_FILE(S3_FILE_PATH, LOCAL_FILE_PATH)
    return LOCAL_FILE_PATH if ok else None

# Make sure the tile list file exists
if not os.path.isfile(TILELIST_FILE):
    print(f"Tile list file '{TILELIST_FILE}' not found. Downloading it now.")
    if DOWNLOAD_FILE('tileList.txt', TILELIST_FILE):
        print(f"'{TILELIST_FILE}' successfully downloaded.")

TILES = LOAD_TILELIST()


def LATLONG_TO_TILE(LAT: float, LON: float) -> tuple[str, str]:
    # Latitude
    if LAT >= 0:
        NORTHING = f"N{int(math.floor(LAT)):02d}_00"
    else:
        NORTHING = f"S{int(abs(math.floor(LAT))):02d}_00"

    # Longitude
    if LON >= 0:
        EASTING = f"E{int(math.floor(LON)):03d}_00"
    else:
        EASTING = f"W{int(abs(math.floor(LON))):03d}_00"

    return NORTHING, EASTING

def CONVERT_TIF_TO_PNG(FILE:str):
    PNG_FILE = os.path.join(HEIGHTMAP_LOCATION, os.path.splitext(os.path.basename(FILE))[0] + ".png")
    with rasterio.open(FILE) as src:
        data = src.read(1).astype(np.float32)

        # NoData maskieren
        if src.nodata is not None:
            data[data == src.nodata] = np.nan

    min_elev = np.nanmin(data)
    max_elev = np.nanmax(data)
    rng = max_elev - min_elev
    if not np.isfinite(rng) or rng == 0:
        raise ValueError("Invalid elevation range (nodata/flat tile).")

    # Clamp + normalize → 16-bit
    data = np.clip(data, min_elev, max_elev)
    norm = (data - min_elev) / rng
    img_16 = (norm * 65535).astype(np.uint16)

    Image.fromarray(img_16, mode="I;16").save(PNG_FILE)
    return PNG_FILE

if __name__ == "__main__":
    args = parse_args()

    if args.lat is not None and args.lon is not None:
        args.northing, args.easting = LATLONG_TO_TILE(args.lat, args.lon)

    try:
        local_tif = DOWNLOAD_TILE(args.northing, args.easting)
        if local_tif:
            png = CONVERT_TIF_TO_PNG(local_tif)
            print("Heightmap:", png)

    except ClientError as e:
        print("Download failed:", e)