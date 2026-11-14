"""Assign a point to a City of Waterloo ward using site/data/wards.geojson."""
import json
import sys
from pathlib import Path

from shapely.geometry import Point, shape

WARDS_PATH = Path(__file__).resolve().parent.parent / "site/data/wards.geojson"


def load_wards() -> list[tuple[int, str, object]]:
    features = json.loads(WARDS_PATH.read_text())["features"]
    return [(int(f["properties"]["WARD_NO"]), f["properties"]["WARD_NAME"], shape(f["geometry"]))
            for f in features]


def assign_ward(lon: float, lat: float) -> int | None:
    """Return the ward number containing (lon, lat), or None if outside the city."""
    pt = Point(lon, lat)
    for number, _name, geom in load_wards():
        if geom.covers(pt):
            return number
    return None


if __name__ == "__main__":
    print(assign_ward(float(sys.argv[1]), float(sys.argv[2])))
