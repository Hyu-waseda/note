# ---------- Makefile ----------
# 変数はお好みで変更してください
INPUT   ?= input.txt
OUTPUT  ?= output.txt

.PHONY: remove generate
remove:
	python remove.py $(INPUT) $(OUTPUT)

generate:
	python generate_prompts.py
# --------------------------------
