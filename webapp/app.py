from flask import Flask, render_template, request, jsonify
import re
import remove  # 同フォルダの既存クリーナーを利用

app = Flask(__name__)

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

    return jsonify({"title": title, "body": body, "hashtags": hashtags})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)
