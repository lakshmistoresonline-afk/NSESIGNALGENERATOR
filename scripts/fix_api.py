from pathlib import Path
p = Path("server/api.py")
text = p.read_text(encoding="utf-8")
text = text.replace("it.get('generation_mode']", "it.get('generation_mode')")
p.write_text(text, encoding="utf-8")
print("Fixed server/api.py successfully.")
