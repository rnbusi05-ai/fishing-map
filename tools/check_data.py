"""指示書 8章のチェックのうち、データで確かめられるものを確認する。

- 全スポットに緯度・経度・情報元URL・確認日がある
- 確かさが決められた3つのどれか
- 確認日から3か月以上たったスポットを一覧にする（調べ直し候補）

使い方: python3 tools/check_data.py
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_kml import ROOT, pin_color, read_spots  # noqa: E402

KAKUSA = {"公式で確認", "釣りブログなど1件", "複数で一致"}


def main():
    errors = 0
    today = datetime.date.today()
    for lake in json.loads((ROOT / "data" / "lakes.json").read_text(encoding="utf-8")):
        spots = read_spots(ROOT / lake["csv"])
        print(f"== {lake['name']}: {len(spots)} 件")
        for s in spots:
            name = s.get("名前") or "(名前なし)"
            problems = []
            try:
                float(s["緯度"]), float(s["経度"])
            except (KeyError, ValueError):
                problems.append("緯度・経度がない")
            if not s.get("情報元URL", "").startswith("http"):
                problems.append("情報元URLがない")
            try:
                checked = datetime.date.fromisoformat(s.get("確認日", ""))
                if (today - checked).days >= 90:
                    print(f"  [調べ直し候補] {name}（確認日 {checked}）")
            except ValueError:
                problems.append("確認日がない（YYYY-MM-DD）")
            if s.get("確かさ") not in KAKUSA:
                problems.append(f"確かさが不正: {s.get('確かさ')!r}")
            for p in problems:
                print(f"  [NG] {name}: {p}")
            errors += len(problems)
            if not problems:
                print(f"  [OK] {name}（{pin_color(s)}）")
    print("問題なし" if errors == 0 else f"問題 {errors} 件")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
