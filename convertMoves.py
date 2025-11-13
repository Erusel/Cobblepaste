import os
import json
import urllib.request
import re

MOVES_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/moves.ts"
OUTPUT_DIR = "static/data"
OUTPUT_JSON = "moves.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

ts_path = os.path.join(OUTPUT_DIR, "moves.ts")
json_path = os.path.join(OUTPUT_DIR, OUTPUT_JSON)

print("Downloading moves.ts...")
urllib.request.urlretrieve(MOVES_URL, ts_path)
print("✔ Download completed")

with open(ts_path, "r", encoding="utf-8") as f:
    content = f.read()


# ---------------------------------------------------------
# REMOVE EXPORT + COMMENTS
# ---------------------------------------------------------

content = re.sub(r"export const Moves[^{]+=", "", content)
content = re.sub(r"//.*", "", content)
content = re.sub(r"/\*[\s\S]*?\*/", "", content)


# Extract only the big object literal
start = content.find("{")
end = content.rfind("}")
content = content[start:end+1]


# ---------------------------------------------------------
# REMOVE ALL TS/JS CALLBACK FUNCTIONS
# ---------------------------------------------------------
# Remove blocks like:
# "key": function(...) { ... },
# key: function(...) { ... },
# key(x,y) { ... },
# key: (x,y) => { ... }

content = re.sub(
    r'[A-Za-z0-9_-]+\s*\([^)]*\)\s*{[^{}]*}',  # namedFunction(arg){...}
    'null',
    content,
    flags=re.S
)

content = re.sub(
    r'"[A-Za-z0-9_-]+"\s*:\s*\([^)]*\)\s*=>\s*{[^{}]*}',
    'null',
    content,
    flags=re.S
)

content = re.sub(
    r'"[A-Za-z0-9_-]+"\s*:\s*function\s*\([^)]*\)\s*{[^{}]*}',
    'null',
    content,
    flags=re.S
)


# ---------------------------------------------------------
# QUOTE ALL KEYS
# ---------------------------------------------------------

content = re.sub(
    r"(?m)^\s*([A-Za-z0-9_-]+)\s*:",
    r'"\1":',
    content
)

content = re.sub(
    r"([{,\[]\s*)([A-Za-z0-9_-]+)\s*:",
    r'\1"\2":',
    content
)


# ---------------------------------------------------------
# FIX SINGLE QUOTED STRINGS → DOUBLE QUOTES
# ---------------------------------------------------------

content = re.sub(
    r"'([^']*)'",
    lambda m: '"' + m.group(1).replace('"', '\\"') + '"',
    content
)


# ---------------------------------------------------------
# REMOVE TRAILING COMMAS
# ---------------------------------------------------------

content = re.sub(r",\s*([}\]])", r"\1", content)


# ---------------------------------------------------------
# PARSE JSON
# ---------------------------------------------------------

try:
    moves = json.loads(content)
except json.JSONDecodeError as e:
    print("❌ JSON ERROR")
    print("Message:", e)
    print("---- around error ----")
    print(content[e.pos-200:e.pos+200])
    raise SystemExit


# ---------------------------------------------------------
# SAVE CLEAN JSON
# ---------------------------------------------------------

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(moves, f, indent=2)

print(f"✔ Conversion successful → {json_path}")
print("Done 🎉")
