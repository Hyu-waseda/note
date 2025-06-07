import os
from dotenv import load_dotenv
from pathlib import Path
from note_client import Note
   # ← ライブラリのモジュール名に合わせて下さい

# 1. 環境変数ロード
load_dotenv()

EMAIL    = os.getenv("NOTE_EMAIL")
PASSWORD = os.getenv("NOTE_PASSWORD")
USER_ID  = os.getenv("NOTE_USER_ID")

if not all([EMAIL, PASSWORD, USER_ID]):
    raise RuntimeError("NOTE_EMAIL / NOTE_PASSWORD / NOTE_USER_ID が設定されていません")

# 2. 3分割ファイル読み込み（remove.py 実行後に存在する前提）
out_dir = Path("output")
title     = (out_dir/"title.txt").read_text("utf-8")
body      = (out_dir/"body.txt" ).read_text("utf-8")
tags_line = (out_dir/"hashtags.txt").read_text("utf-8")
tags      = tags_line.strip().split()

# 3. NoteClient でログイン & 下書き作成
note = Note(email=EMAIL, password=PASSWORD, user_id=USER_ID)

note.create_article(
    title           = title,
    file_name       = out_dir/"body.txt",   # 本文ファイルを渡す実装が多い
    input_tag_list  = tags,
    post_setting    = False,                # False = 草稿 / 下書き
    headless        = True                  # ブラウザを開かない
)

print("✅ note に下書きを保存しました")