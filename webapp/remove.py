#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remove.py — note 用 Markdown クリーナー ＋ 3 分割出力
（タイトル先頭の # マーク削除対応版）
────────────────────────────────────────
● 出力を 1 ファイル → 3 ファイルへ分割
   ├ hashtags.txt : 自動生成したハッシュタグ列
   ├ title.txt    : 最初の Markdown 見出し行（# …）※# は除去
   └ body.txt     : タイトル以降の本文＋ディスクレーマー
● 旧 output.txt は生成しない
● コマンドラインを省略可
────────────────────────────────────────
"""

import os
import sys
import re
import shutil
from datetime import datetime

import webbrowser          # ブラウザ起動
import pyperclip           # クリップボード操作
import time 


# -------------------------------------------------------------
# 0  HTML ライクなペアタグ <tag>…</tag> の角括弧だけ除去
# -------------------------------------------------------------
HTML_PAIR = re.compile(r"<([A-Za-z][A-Za-z0-9]*)\b[^>]*>(.*?)</\1>", re.DOTALL)

def strip_html_pairs(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = HTML_PAIR.sub(lambda m: m.group(2), text)
    return text

# -------------------------------------------------------------
# 1  見出し行内の **bold** を除去
# -------------------------------------------------------------
HEADING_BOLD_LINE = re.compile(r"^(?P<prefix>[ \t]*#+\s*)(?P<body>.*)$", re.MULTILINE)
BOLD_INLINE = re.compile(r'\*\*([^"\n]*?)\*\*')

def strip_bold_in_headings(text: str) -> str:
    def _repl(match):
        prefix, body = match.group('prefix'), match.group('body')
        body_clean = BOLD_INLINE.sub(r"\1", body)
        return f"{prefix}{body_clean}"
    return HEADING_BOLD_LINE.sub(_repl, text)

# -------------------------------------------------------------
# 2  かっこ削除（引用／URL／[] を含むもの）
# -------------------------------------------------------------
PAREN_PATTERN = re.compile(r"\s*\([^)]*(?:\[[^\]]+]|https?://)[^)]*\)")

def clean_parentheses(text: str) -> str:
    text = PAREN_PATTERN.sub('', text)
    text = re.sub(r"\s*\(\s*\)", '', text)
    text = re.sub(r"\)\s*(?=[。、，…\.\,\)]|\n|$)", '', text)
    return re.sub(r"[ \t]{2,}", ' ', text)

# -------------------------------------------------------------
# 3 '**   xxx   **' → '**xxx**'
# -------------------------------------------------------------
INNER_BOLD = re.compile(r"\*\*[\s\u3000]*([^\*]+?)[\s\u3000]*\*\*")

def strip_inner_spaces(text: str) -> str:
    return INNER_BOLD.sub(lambda m: f"**{m.group(1)}**", text)

# -------------------------------------------------------------
# 4 '**xxx**' を前後 1 空白に包む
# -------------------------------------------------------------
def pad_bold_uniformly(text: str) -> str:
    text = re.sub(r"\*\*([^\*]+?)\*\*", r" **\1** ", text)
    text = re.sub(r" *\n", '\n', text)
    text = re.sub(r"\n *", '\n', text)
    return text

# -------------------------------------------------------------
# 5 行途中の '## ' を見出し化
# -------------------------------------------------------------
def ensure_heading_newline(text: str) -> str:
    return re.sub(r"\n(?!\n)(##\s+)", r"\n\n\1", text)

# -------------------------------------------------------------
# 6 前書きを削除
# -------------------------------------------------------------
def drop_preamble(text: str) -> str:
    m = re.search(r"(?m)^[ \t]*#+\s", text)
    return text[m.start():] if m else text

# -------------------------------------------------------------
# 2a  バックスラッシュ付き '**' を正規 '**' に戻す
# -------------------------------------------------------------
def unescape_bold(text: str) -> str:
    return text.replace(r"\*\*", "**")

# -------------------------------------------------------------
# 7 文章中の「X月X日時点」を今日に置換
# -------------------------------------------------------------
AS_OF_PATTERN = re.compile(r"[0-9０-９]{1,2}月[0-9０-９]{1,2}日時点")

def update_as_of_date(text: str) -> str:
    today = datetime.now()
    today_str = f"{today.month}月{today.day}日時点"
    return AS_OF_PATTERN.sub(today_str, text)

# -------------------------------------------------------------
# クレンジングパイプライン
# -------------------------------------------------------------
def clean_text(raw: str) -> str:
    txt = drop_preamble(raw)
    txt = unescape_bold(txt)
    txt = strip_html_pairs(txt)
    txt = strip_bold_in_headings(txt)
    txt = update_as_of_date(txt)
    txt = clean_parentheses(txt)
    txt = strip_inner_spaces(txt)
    txt = pad_bold_uniformly(txt)
    txt = ensure_heading_newline(txt)
    return txt.rstrip('\n') + '\n'

# -------------------------------------------------------------
# 企業名・タグ関連（フルリスト）
# -------------------------------------------------------------
COMPANIES = [
    'トヨタ自動車','ソニーグループ','東京エレクトロン','ソフトバンクグループ','任天堂',
    '三菱UFJFG','三菱UFJ','ファーストリテイリング','ユニ・チャーム','武田薬品工業','三菱商事',
    '本田技研工業','キーエンス','SUMCO','日本電信電話','NTT','バンダイナムコHD',
    '三井住友FG','三井住友フィナンシャルグループ','セブン＆アイHD','花王','アステラス製薬','三井物産',
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
    "#株式投資 #株 #株価 #業績 #投資 #銘柄分析 #資産運用 #新NISA #NISA #経済 #企業"
)

def detect_company(text: str) -> str:
    earliest_pos = len(text) + 1
    selected = 'その他'
    for name in COMPANIES:
        pos = text.find(name)
        if pos != -1 and (pos < earliest_pos or (pos == earliest_pos and len(name) > len(selected))):
            earliest_pos = pos
            selected = name
            if earliest_pos == 0:
                break
    return selected

def build_hashtags(company: str) -> str:
    return HASH_TAGS + (f" #{company}" if company != "その他" else "")

# -------------------------------------------------------------
# 出力 & ログ保存
# -------------------------------------------------------------
def save_outputs_and_logs(in_path: str,
                          out_dir : str,
                          hashtags: str,
                          title   : str,
                          body    : str,
                          raw     : str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    files = {
        'hashtags.txt': hashtags,
        'title.txt'   : title,
        'body.txt'    : body,
    }
    for fname, content in files.items():
        with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
            f.write(content)

    company = detect_company(body)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = os.path.join('log', f'{ts}_{company}')
    os.makedirs(log_dir, exist_ok=True)

    shutil.copy2(in_path, os.path.join(log_dir, 'input.txt'))
    for fname in files:
        shutil.copy2(os.path.join(out_dir, fname),
                     os.path.join(log_dir, fname))

# -------------------------------------------------------------
# クリップボード & note 新規記事タブを開く
# -------------------------------------------------------------
def copy_to_clipboard_sequence(title: str, hashtags: str, body: str) -> None:
    seq = [title, hashtags, body]
    for item in seq:
        pyperclip.copy(item)
        # macOS: 0.5秒、Windows: 1秒くらい余裕があると安心
        time.sleep(0.5)


# -------------------------------------------------------------
# エントリポイント
# -------------------------------------------------------------
def main(in_path: str, out_dir: str) -> None:
    if not os.path.exists(in_path):
        raise FileNotFoundError(in_path)

    with open(in_path, encoding="utf-8") as f:
        raw = f.read()

    company   = detect_company(raw)
    hashtags  = build_hashtags(company) + '\n'
    cleaned   = clean_text(raw)

    first_nl   = cleaned.find('\n')
    title_line = cleaned[:first_nl].rstrip() if first_nl != -1 else cleaned.rstrip()
    title_line = re.sub(r'^[ \t]*#+\s*', '', title_line)      # ← # を除去

    body_part  = cleaned[first_nl+1:].lstrip('\n') if first_nl != -1 else ''
    body_text  = f"{body_part.rstrip()}\n\n{DISCLAIMER}\n"    # ← body は改行ありで OK

    # ★ ここで末尾改行を落としておく
    hashtags_no_nl = hashtags.rstrip('\n')
    title_no_nl    = title_line           # 末尾改行は付けない

    save_outputs_and_logs(
        in_path, out_dir,
        hashtags_no_nl,                  # ← 改行なし
        title_no_nl,                     # ← 改行なし
        body_text,
        raw
    )
    print(f"✔ 出力先: {out_dir}\n✔ ログ保存完了")
    
	# 既存のログ保存メッセージ
    print(f"✔ 出力先: {out_dir}\n✔ ログ保存完了")

    # クリップボード三段コピー＋ブラウザで note を開く
    copy_to_clipboard_sequence(title_line, hashtags_no_nl, body_text)
    webbrowser.open_new_tab("https://note.com/notes/new")
    print("📋 タイトル → ハッシュタグ → 本文 の順にクリップボードへコピー済み")
    print("ブラウザで新規記事タブが開きました。エディタで 3 回貼り付ければ完成です！")


# -------------------------------------------------------------
# スクリプト直接実行
# -------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    input_path = 'input.txt'
    output_dir = 'output'

    if len(args) == 1:
        input_path = args[0]
    elif len(args) == 2:
        input_path, out_arg = args
        if out_arg.lower().endswith('.txt') or (os.path.exists(out_arg) and os.path.isfile(out_arg)):
            output_dir = os.path.splitext(out_arg)[0]  # output.txt → output/
        else:
            output_dir = out_arg
    elif len(args) > 2:
        print("Usage:\n"
              "  python remove.py                 # input.txt → ./output/\n"
              "  python remove.py <in>            # <in>     → ./output/\n"
              "  python remove.py <in> <out>      # <in>     → <out_dir|derived>/")
        sys.exit(1)

    main(input_path, output_dir)
