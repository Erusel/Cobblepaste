import json
import json5

input_path = "./static/data/abilities.json"
output_path = "static/data/abilities.json"

with open(input_path, "r", encoding="utf8") as f:
    data = json5.load(f)   # <- JSON5 PARSER (magique)

with open(output_path, "w", encoding="utf8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✔ Converted to proper JSON!")
