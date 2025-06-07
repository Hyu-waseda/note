#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bold_debug.py  ― まずは太字だけ動作確認

1) strip_inner_spaces : '**   xxx  **'  → '**xxx**'
2) pad_bold_uniformly : '**xxx**'       → ' **xxx** '

※改行や見出し処理は一切入れていません
"""

import re

# -------------------------------------------------------------
# ① 内側スペース除去
#   - 半角 / 全角スペースどちらもまとめて吸収
# -------------------------------------------------------------
def strip_inner_spaces(text: str) -> str:
    pattern = re.compile(r'\*\*[\s\u3000]*([^\*]+?)[\s\u3000]*\*\*')
    return pattern.sub(lambda m: f'**{m.group(1)}**', text)

# -------------------------------------------------------------
# ② 外側スペースを必ず 1 個ずつ追加
#   - 改行は壊さない（置換前後で改行文字に触れない）
# -------------------------------------------------------------
def pad_bold_uniformly(text: str) -> str:
    return re.sub(r'\*\*([^\*]+?)\*\*', r' **\1** ', text)

# -------------------------------------------------------------
if __name__ == '__main__':
    tests = {
        "A": "**東京エレクトロン** と **株価**",
        "B": "** 東京エレクトロン ** と ** 株価 **",
        "C": "**　東京エレクトロン　** と **　株価　**",
        "D": "成長**戦略**を検証",
        "E": "**+65%** 増"
    }

    for k, raw in tests.items():
        step1 = strip_inner_spaces(raw)
        step2 = pad_bold_uniformly(step1)
        print(f"\n=== Test {k} =============================")
        print("RAW :", raw)
        print("① strip_inner :", step1)
        print("② pad_bold    :", step2)
