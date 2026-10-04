"""data/lakes.json に載っている湖ごとに、CSV から kml/<id>.kml を作る。

使い方: python3 tools/build_kml.py
"""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

# ピンの色のルール（index.html と同じ）
NO_CAUTION = {"", "未確認", "なし", "特になし"}
# KML の色は aabbggrr
KML_COLORS = {"red": "ff3a3ad6", "green": "ff4a9d2e", "yellow": "ff00b0e0"}
FIELDS = ["足場", "駐車場", "トイレ", "最寄りバス停", "注意", "情報元URL", "確認日", "確かさ"]


def has_caution(s):
    return s.get("注意", "").strip() not in NO_CAUTION


def pin_color(s):
    if has_caution(s):
        return "red"
    if s.get("確かさ", "").strip() in ("公式で確認", "複数で一致"):
        return "green"
    return "yellow"


def read_spots(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def build(lake):
    spots = read_spots(ROOT / lake["csv"])
    styles = "".join(
        f'<Style id="{name}"><IconStyle><color>{color}</color>'
        "<Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href></Icon>"
        "</IconStyle></Style>"
        for name, color in KML_COLORS.items()
    )
    marks = []
    for s in spots:
        try:
            lat, lng = float(s["緯度"]), float(s["経度"])
        except (KeyError, ValueError):
            continue
        desc = "\n".join(f"{k}: {s.get(k) or '未確認'}" for k in FIELDS)
        data = "".join(
            f'<Data name="{escape(k)}"><value>{escape(s.get(k) or "未確認")}</value></Data>' for k in FIELDS
        )
        marks.append(
            f"<Placemark><name>{escape(s['名前'])}</name>"
            f"<description>{escape(desc)}</description>"
            f"<styleUrl>#{pin_color(s)}</styleUrl>"
            f"<ExtendedData>{data}</ExtendedData>"
            f"<Point><coordinates>{lng},{lat},0</coordinates></Point></Placemark>"
        )
    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
        f"<name>{escape(lake['name'])} ショアスポット</name>{styles}{''.join(marks)}"
        "</Document></kml>\n"
    )
    out = ROOT / "kml" / f"{lake['id']}.kml"
    out.write_text(kml, encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(marks)} 件")


def main():
    for lake in json.loads((ROOT / "data" / "lakes.json").read_text(encoding="utf-8")):
        build(lake)


if __name__ == "__main__":
    main()
