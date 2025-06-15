from flask import Flask, render_template, request, jsonify
import re
import json
import os
from datetime import datetime
import uuid
import remove  # 同フォルダの既存クリーナーを利用

app = Flask(__name__)

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs.jsonl")


def append_log(entry: dict) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")


def read_logs() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/clean", methods=["POST"])
def clean():
    raw = request.form.get("markdown", "")
    if not raw.strip():
        return jsonify({"error": "empty"}), 400

    # remove.py の関数を活用
    cleaned = remove.clean_text(raw)
    first_nl = cleaned.find("\n")
    title = cleaned[:first_nl].strip() if first_nl != -1 else cleaned.strip()
    title = re.sub(r"^[ \t]*#+\s*", "", title)

    body_part = cleaned[first_nl + 1 :].lstrip() if first_nl != -1 else ""
    body = f"{body_part.strip()}\n\n{remove.DISCLAIMER}\n"

    company = remove.detect_company(raw)
    hashtags = remove.build_hashtags(company)

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "input": raw,
        "title": title,
        "body": body,
        "hashtags": hashtags,
    }
    append_log(entry)

    return jsonify({"title": title, "body": body, "hashtags": hashtags})


@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(read_logs())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)
