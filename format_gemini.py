#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
format_gemini.py — note 用 Markdown クリーナー
  * 既存 remove.py の全機能を継承
  * 追加: 文末の「 半角／全角スペース + 数字 + 句点（ 。 . ）」を除去
  * 入出力ファイル名をハードコード（input.txt → output.txt）
      ‣ ０引数 : 上記デフォルトを使用
      ‣ ２引数 : <in> <out> を指定
"""

import os
import sys
import re
import shutil
from datetime import datetime

# ──────────────────────────────────────────
# ⑦ 文末「 数字＋句点」を削除               ★追加★
TRAILING_NUM_PATTERN = re.compile(r"\s+[0-9０-９]+(?=[。\.])")
def remove_trailing_numbers(text: str) -> str:
    """例: '発表しました 8。' → '発表しました。'"""
    return TRAILING_NUM_PATTERN.sub("", text)

# ──────────────────────────────────────────
# ① かっこ削除（引用／URL／[] を含むもの）
PAREN_PATTERN = re.compile(r"\s*\([^)]*(?:\[[^\]]+]|https?://)[^)]*\)")
def clean_parentheses(text: str) -> str:
    text = PAREN_PATTERN.sub("", text)
    text = re.sub(r"\s*\(\s*\)", "", text)  # 空 ()
    text = re.sub(r"\)\s*(?=[。、，…\.\,\)]|\n|$)", "", text)  # 単独 ')'
    return re.sub(r"[ \t]{2,}", " ", text)

# ② '**   xxx   **' → '**xxx**'
INNER_BOLD = re.compile(r"\*\*[\s\u3000]*([^\*]+?)[\s\u3000]*\*\*")
def strip_inner_spaces(text: str) -> str:
    return INNER_BOLD.sub(lambda m: f"**{m.group(1)}**", text)

# ③ '**xxx**' の前後を 1 空白に統一
def pad_bold_uniformly(text: str) -> str:
    text = re.sub(r"\*\*([^\*]+?)\*\*", r" **\1** ", text)
    text = re.sub(r" *\n", "\n", text)   # 行末空白
    text = re.sub(r"\n *", "\n", text)   # 行頭空白
    return text

# ④ 行途中 '## ' 見出しの前に空行
def ensure_heading_newline(text: str) -> str:
    return re.sub(r"\n(?!\n)(##\s+)", r"\n\n\1", text)

# ⑤ 最初の Markdown 見出しより前を削除
def drop_preamble(text: str) -> str:
    m = re.search(r"(?m)^[ \t]*#+\s", text)
    return text[m.start():] if m else text

# ⑥ 「X月X日時点」を今日に更新
AS_OF_PATTERN = re.compile(r"[0-9０-９]{1,2}月[0-9０-９]{1,2}日時点")
def update_as_of_date(text: str) -> str:
    today = datetime.now()           # Asia/Tokyo
    today_str = f"{today.month}月{today.day}日時点"
    return AS_OF_PATTERN.sub(today_str, text)

# ──────────────────────────────────────────
# 企業リスト・ハッシュタグ・免責
COMPANIES = [
    'トヨタ自動車','ソニーグループ','東京エレクトロン','ソフトバンクグループ','任天堂',
    '三菱UFJFG','三菱UFJ','ファーストリテイリング','ユニ・チャーム','武田薬品工業','三菱商事',
    '本田技研工業','キーエンス','SUMCO','日本電信電話','NTT','バンダイナムコHD',
    '三井住友FG','セブン＆アイHD','花王','アステラス製薬','三井物産',
    '日産自動車','日立製作所','ルネサスエレクトロニクス','KDDI','カプコン',
    'みずほFG','イオン','キリンHD','第一三共','伊藤忠商事','スズキ','パナソニックHD',
    'アドバンテスト','ソフトバンク','スクウェア・エニックスHD','オリックス','PPIH',
    'アサヒグループHD','エーザイ','住友商事','マツダ','NEC','信越化学工業','メルカリ',
    'コナミグループ','第一生命HD','ローソン','サッポロHD','中外製薬','丸紅','SUBARU',
    '富士通','ファナック','サイバーエージェント','コーエーテクモHD','東京海上HD',
    '三越伊勢丹HD','サントリー食品','塩野義製薬','豊田通商','三菱自動車工業',
    'キヤノン','村田製作所','LY','野村HD','J.フロントリテイリング','日清食品HD',
    '大塚HD','コマツ','いすゞ自動車','ニコン','ディー・エヌ・エー','SBIホールディングス',
    '良品計画','味の素','小野薬品工業','ダイキン工業','ヤマハ発動機','三菱電機','りそなHD',
    'ZOZO','キッコーマン','日本新薬','安川電機','日野自動車','ゆうちょ銀行','ツルハHD',
    'カルビー','JCRファーマ','三菱重工業','日本取引所グループ','明治HD','JR東日本',
    '大和証券G','ヤクルト本社','ANAホールディングス','日本郵政','東京電力HD',
    '三井住友トラストHD','楽天銀行'
]

DISCLAIMER = (
    "※本記事は銘柄に関する情報をもとに分析を行ったものであり、"
    "特定の投資行動を推奨するものではありません。"
    "投資に関する最終的な判断は、ご自身の責任にてお願いいたします。"
)

HASH_TAGS = (
    "#株式投資"
    " #株"
    " #株価"
    " #業績"
    " #投資"
    " #銘柄分析"
    " #資産運用"
    " #新NISA"
    " #NISA"
    " #経済"
    " #企業"
)

def detect_company(text: str) -> str:
    for name in sorted(COMPANIES, key=len, reverse=True):
        if name in text:
            return name
    return "その他"

def build_hashtags(company: str) -> str:
    return HASH_TAGS + (f" #{company}" if company != "その他" else "")

def save_logs(in_path: str, out_path: str, body: str) -> None:
    company   = detect_company(body)
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir   = os.path.join("log", f"{ts}_{company}")
    os.makedirs(log_dir, exist_ok=True)
    shutil.copy2(in_path,  os.path.join(log_dir, "input.txt"))
    shutil.copy2(out_path, os.path.join(log_dir, "output.txt"))

# ──────────────────────────────────────────
def clean_text(raw: str) -> str:
    txt = drop_preamble(raw)
    txt = update_as_of_date(txt)
    txt = clean_parentheses(txt)
    txt = strip_inner_spaces(txt)
    txt = pad_bold_uniformly(txt)
    txt = ensure_heading_newline(txt)
    txt = remove_trailing_numbers(txt)     # ★ 追加ステップ
    return txt.rstrip("\n") + "\n"

# ──────────────────────────────────────────
def main(in_path: str, out_path: str) -> None:
    if not os.path.exists(in_path):
        raise FileNotFoundError(in_path)

    with open(in_path, encoding="utf-8") as f:
        raw = f.read()

    company  = detect_company(raw)
    cleaned  = build_hashtags(company) + "\n" + clean_text(raw) + "\n" + DISCLAIMER

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    save_logs(in_path, out_path, raw)
    print(f"✔ 出力: {out_path}\n✔ ログ保存完了")

# ──────────────────────────────────────────
if __name__ == "__main__":
    default_in, default_out = "input.txt", "output.txt"  # ← ハードコード
    if len(sys.argv) == 1:
        main(default_in, default_out)
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Usage:")
        print("  python format_gemini.py            # input.txt → output.txt")
        print("  python format_gemini.py <in> <out>")
        sys.exit(1)
