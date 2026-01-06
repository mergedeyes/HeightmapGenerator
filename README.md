# Copernicus DEM Heightmap Generator

A small Python tool to download **Copernicus DEM (GLO-30)** tiles from the public AWS S3 bucket and convert them into **16-bit grayscale heightmap PNGs**.

Supports direct tile selection (N47_00 E009_00) or automatic conversion from **latitude/longitude**, including **auto exposure**.

---

## Features

- Download Copernicus DEM tiles (30 m resolution)
- No login, no API key (public S3 bucket)
- Convert GeoTIFF to **16-bit heightmap PNG**
- Auto exposure (--auto): lowest elevation = black, highest = white
- Manual min/max elevation supported
- Latitude / Longitude to tile conversion
- Tile availability check via tileList.txt

---

## Requirements

- Python 3.10+
- Dependencies:
  - boto3
  - rasterio
  - numpy
  - pillow

Install:

    pip install boto3 rasterio numpy pillow

Arch Linux (recommended):

    sudo pacman -S python-boto3 python-rasterio python-numpy python-pillow gdal

---

## Usage

### Download by tile name

    python app.py --northing N47_00 --easting E009_00

### Download by latitude / longitude

    python app.py --lat 47.62 --lon 9.48

### Auto exposure

    python app.py --lat 47.62 --lon 9.48 --auto

### Manual elevation range

    python app.py --lat 47.62 --lon 9.48 --min -100 --max 3000

---

## Output

GeoTIFF files:

    data/tif/

Heightmap PNG files (16-bit):

    data/heightmaps/

Suitable for:
- Game engines
- Terrain tools
- Blender
- GIS workflows

---

## Notes

- Heightmaps are **true 16-bit**, not 8-bit images
- No resampling or smoothing
- NoData values are ignored automatically
- Tiles are cached locally and not downloaded twice

---

## License

Copernicus DEM data: Public Domain  
Code license: GNU GENERAL PUBLIC LICENSE

---

# Copernicus DEM Heightmap Generator (Deutsch)

Ein kleines Python-Tool zum Herunterladen von **Copernicus DEM (GLO-30)** Höhenmodellen aus dem öffentlichen AWS-S3-Bucket und zur Umwandlung in **16-Bit Graustufen-Heightmaps**.

---

## Funktionen

- Download von Copernicus DEM Tiles (30 m Auflösung)
- Kein Login, kein API-Key erforderlich
- GeoTIFF zu **16-Bit Heightmap PNG**
- Auto Exposure (--auto): niedrigster Punkt = schwarz, höchster = weiß
- Manuelle Höhenbegrenzung möglich
- Latitude / Longitude zu Tile-Berechnung
- Tile-Verfügbarkeit über tileList.txt

---

## Voraussetzungen

- Python 3.10+
- Abhängigkeiten:
  - boto3
  - rasterio
  - numpy
  - pillow

Installation:

    pip install boto3 rasterio numpy pillow
Arch Linux (empfohlen):

    sudo pacman -S python-boto3 python-rasterio python-numpy python-pillow gdal

---

## Verwendung

### Download über Tile-Namen

    python app.py --northing N47_00 --easting E009_00

### Download über Koordinaten

    python app.py --lat 47.62 --lon 9.48

### Auto Exposure

    python app.py --lat 47.62 --lon 9.48 --auto

### Manuelle Höhenbegrenzung

    python app.py --lat 47.62 --lon 9.48 --min -100 --max 3000

---

## Ausgabe

GeoTIFF-Dateien:

    data/tif/

Heightmap-PNGs (16-Bit):

    data/heightmaps/

---

## Hinweise

- Echte **16-Bit Heightmaps**, keine 8-Bit Bilder
- Keine Glättung oder Interpolation
- NoData-Werte werden automatisch ignoriert
- Bereits geladene Tiles werden wiederverwendet

---

## Lizenz

Daten: Public Domain (Copernicus DEM)  
Code: GNU GENERAL PUBLIC LICENSE
