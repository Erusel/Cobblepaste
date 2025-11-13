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

    # CLEAN HEADER (.rs, .rv, .s etc.)
    header = lines[0].lstrip()
    if header.startswith("."):
        return {}  # hard skip any command header

    # Strip leading dot-tags inside nickname
    if header.lower().startswith(".rs "):
        header = header[4:].lstrip()
    if header.lower().startswith(".rv "):
        header = header[4:].lstrip()
    if header.lower().startswith(".s "):
        header = header[3:].lstrip()

    lines[0] = header

    # ITEM
    item = None
    first = lines[0]
    if "@" in first:
        left, item = first.split("@", 1)
        left = left.strip()
        item = item.strip()
    else:
        left = first.strip()

    # NICKNAME / SPECIES
    nickname = None
    species = None

    if "(" in left and left.endswith(")"):
        nickname = left.split("(", 1)[0].strip()
        species = left[left.find("(") + 1 : -1].strip()
    else:
        species = left

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

        # Remove standalone commands (.rs, .S, etc.)
        if stripped.startswith(".") and len(stripped.split()) == 1:
            continue

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)

    # split blocks
    blocks = re.split(r"\n\s*\n", cleaned.strip())

    team: List[Dict[str, Any]] = []

    for block in blocks:
        first_line = block.strip().split("\n", 1)[0].strip()

        # ignore ANY block starting with "."
        if first_line.startswith("."):
            continue

        mon = parse_pokemon_block(block)

        # Only keep valid mons
        if mon.get("species") and mon.get("moves"):
            team.append(mon)

    return team
