#!/usr/bin/env python3
"""
template.txt の <企業名> / <銘柄番号> を company_schedule_100days.csv で
置き換え、prompts/<Day>_<企業名>.md を生成
"""

from pathlib import Path
import csv, re
from datetime import date          # ① 追加ここだけ

# ======== 設定ここだけ ========
TEMPLATE_FILE = Path("template.txt")
CSV_FILE      = Path("company_schedule_100days.csv")
OUTPUT_DIR    = Path("prompts")
# ===============================

def sanitize(name: str) -> str:
    """ファイル名に使えない文字（スラッシュなど）を置換"""
    return re.sub(r"[\\/:*?\"<>|]", "_", name)

def main() -> None:
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, start=1):
            # ---- Day 列が無いときは enumerate で補完 ----
            day_str = row.get("Day") or row.get("day") or str(i)
            day     = int(day_str)

            company = row.get("Company") or row.get("company")
            code    = row.get("Code")    or row.get("code")
            if company is None or code is None:
                raise ValueError(
                    f"列名が見つかりません。reader fieldnames = {reader.fieldnames}"
                )

            filled = (
                template
                .replace("<企業名>", company)
                .replace("<銘柄番号>", code)
            )
            # ② 今日の日付を追記
            today_str = date.today().strftime("%Y年%m月%d日")
            filled += f"\n- 現在の日付は{today_str}です。ただし、記事の投稿が今日とは限らないので、記事内で言及は避けてください。\n"

            filename = f"{day:02d}_{sanitize(company)}.md"
            (OUTPUT_DIR / filename).write_text(filled, encoding="utf-8")
            print(f"✔ created {filename}")

if __name__ == "__main__":
    main()
