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
        help="Northing tile, e.g. N47_00"
    )
    parser.add_argument(
        "--easting",
        required=False,
        help="Easting tile, e.g. E009_00"
    )

    return parser.parse_args()

def CHECK_FILE(FILE:str):
    return os.path.isfile(FILE)

# Define Download Functionality
def DOWNLOAD_FILE(OBJECT_NAME: str, FILE_NAME: str):
    try:
        with open(FILE_NAME, "wb") as f:
            s3.download_fileobj(S3_BUCKET_BASE, OBJECT_NAME, f)
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
    if TILE_AVAILABLE(S3_BASE_STR):
        return DOWNLOAD_FILE(S3_FILE_PATH, LOCAL_FILE_PATH)
    return (False)

# Make sure the tile list file exists
if not os.path.isfile(TILELIST_FILE):
    print(f"Tile list file '{TILELIST_FILE}' not found. Downloading it now.")
    if DOWNLOAD_FILE('tileList.txt', TILELIST_FILE):
        print(f"'{TILELIST_FILE}' successfully downloaded.")

TILES = LOAD_TILELIST()

if __name__ == "__main__":
    args = parse_args()
    if args.northing == None and args.easting == None:
        print("Test download...")
    if args.northing == None:
        args.northing = DEFAULT_NORTHING
        print("No argument for northing, setting default:", DEFAULT_NORTHING)
    if args.easting == None:
        args.easting = DEFAULT_EASTING
        print("No argument for easting, setting default:", DEFAULT_EASTING)

    try:
        if DOWNLOAD_TILE(args.northing, args.easting):
            print(
                f"File {os.path.join(TIF_LOCATION, f'{args.northing}_{args.easting}.tif')} successfully downloaded."
            )
    except ClientError as e:
        print("Download failed:", e)