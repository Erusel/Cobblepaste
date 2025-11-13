import re
from typing import List, Dict, Any


def normalise_sprite_name(species: str) -> str:
    name = species.lower()
    name = name.replace(" ", "-")
    name = name.replace(".", "")
    name = name.replace("'", "")
    name = name.replace("é", "e")
    name = name.replace("♀", "-f")
    name = name.replace("♂", "-m")
    return name


def parse_evs_or_ivs(line: str) -> Dict[str, int]:
    # "EVs: 252 SpA / 4 SpD / 252 Spe"
    _, values = line.split(":", 1)
    parts = [p.strip() for p in values.split("/") if p.strip()]
    result: Dict[str, int] = {}

    for part in parts:
        match = re.match(r"(\d+)\s+(.+)", part)
        if match:
            value = int(match.group(1))
            stat = match.group(2)
            result[stat] = value

    return result


def parse_pokemon_block(block: str) -> Dict[str, Any]:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    if not lines:
        return {}

    # --- CLEAN FIRST LINE OF BLOCK (remove .RS etc inside nickname/species) ---
    header = lines[0].lstrip()

    # remove leading dot-commands like ".RS Team", ".rv lead", ".S test"
    if header.lower().startswith(".rs "):
        header = header[4:].lstrip()
    elif header.lower().startswith(".rv "):
        header = header[4:].lstrip()
    elif header.lower().startswith(".s "):
        header = header[3:].lstrip()
    elif header.startswith("."):
        # generic fallback: remove first word beginning with "."
        parts = header.split(" ", 1)
        if len(parts) > 1:
            header = parts[1].lstrip()

    lines[0] = header  # update header

    # --- ITEM SPLIT ---
    first = lines[0]
    item = None

    if "@" in first:
        left, item = first.split("@", 1)
        left = left.strip()
        item = item.strip()
    else:
        left = first.strip()

    # --- NICKNAME / SPECIES ---
    nickname = None
    species = None

    # Format: Nick (Species)
    if "(" in left and left.endswith(")"):
        nickname = left.split("(", 1)[0].strip()
        species = left[left.find("(") + 1 : -1].strip()
    else:
        species = left

    # --- Stats ---
    ability = None
    nature = None
    tera_type = None
    evs = {}
    ivs = {}
    moves: List[str] = []

    for line in lines[1:]:
        if line.startswith("Ability:"):
            ability = line.split(":", 1)[1].strip()

        elif line.startswith("EVs:"):
            evs = parse_evs_or_ivs(line)

        elif line.startswith("IVs:"):
            ivs = parse_evs_or_ivs(line)

        elif line.startswith("Tera Type:"):
            tera_type = line.split(":", 1)[1].strip()

        elif line.endswith("Nature"):
            nature = line.replace("Nature", "").strip()

        elif line.startswith("- "):
            moves.append(line[2:].strip())

    return {
        "nickname": nickname,
        "species": species,
        "item": item,
        "ability": ability,
        "nature": nature,
        "tera_type": tera_type,
        "evs": evs,
        "ivs": ivs,
        "moves": moves,
        "sprite_name": normalise_sprite_name(species),
    }


def parse_showdown_team(paste: str) -> List[Dict[str, Any]]:
    cleaned_lines = []

    for line in paste.splitlines():
        stripped = line.strip()

        # remove blank dot-commands
        if stripped.startswith(".") and len(stripped) <= 4:
            continue

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)

    # split Pokémon blocks by blank lines
    blocks = re.split(r"\n\s*\n", cleaned.strip())

    team: List[Dict[str, Any]] = []

    for block in blocks:
        # Skip blocks that are just labels or garbage like ".rs Veil Team"
        first_line = block.strip().split("\n", 1)[0].strip()

        # skip if it begins with a dot-command
        if first_line.startswith("."):
            continue

        # skip if it contains no item, no ability, no nature, no dash lines
        if ("@" not in block) and ("Ability:" not in block) and ("Nature" not in block):
            continue

        mon = parse_pokemon_block(block)
        if mon.get("species"):
            team.append(mon)

    return team
