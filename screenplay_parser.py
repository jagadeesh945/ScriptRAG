import re
from typing import List, Dict, Any, Set, Tuple

# Common screenplay slugline prefixes
SCENE_HEADING_REGEX = re.compile(
    r'^\s*(?:[0-9]{1,3}\s+)?(?:\.)?\s*(INT\./EXT\.|EXT\./INT\.|INT/EXT|EXT/INT|INT\.|EXT\.|INT|EXT)\s+([^-\n]+?)(?:\s*-\s*|\s+-\s+)(.+)$',
    re.IGNORECASE
)

# Common transitions and non-character capitalized lines
NON_CHARACTER_WORDS = {
    "FADE IN:", "FADE OUT.", "FADE OUT", "CUT TO:", "DISSOLVE TO:", "SMASH CUT TO:",
    "MATCH CUT TO:", "BACK TO:", "JUMP CUT TO:", "FLASHBACK:", "END FLASHBACK",
    "THE END", "CONTINUED:", "CONTINUED", "(CONTINUED)", "BLACK", "TITLES", "SUPER:",
    "MONTAGE", "CREDITS", "INTERCUT", "SERIES OF SHOTS", "CLOSE UP", "WIDE SHOT", "ANGLE ON"
}

ROLE_KEYWORDS = {
    "OFFICER", "COP", "GUARD", "SOLDIER", "PILOT", "DOCTOR", "NURSE", "WAITER",
    "WAITRESS", "BARTENDER", "AGENT", "MAN", "WOMAN", "BOY", "GIRL", "CHILD",
    "DRIVER", "FARMER", "CLERK", "DETECTIVE", "REPORTER", "SECRETARY", "VOICE", "TECHNICIAN"
}

def clean_character_name(raw_name: str) -> Tuple[str, str, bool]:
    """
    Parses character cue, separating canonical name, modifier/parenthetical, and voice/off-screen status.
    Returns: (cleaned_name, modifier, is_offscreen)
    """
    cleaned = raw_name.strip()
    is_offscreen = False
    modifier = ""

    # Check for (V.O.), (O.S.), (O.C.), (CONT'D), etc.
    paren_matches = re.findall(r'\((.*?)\)', cleaned)
    if paren_matches:
        for p in paren_matches:
            p_upper = p.upper()
            if any(term in p_upper for term in ["V.O.", "VOICE OVER", "O.S.", "OFF SCREEN", "O.C."]):
                is_offscreen = True
            modifier += f" ({p})"
        cleaned = re.sub(r'\(.*?\)', '', cleaned).strip()

    # Strip numbers or trailing punctuation
    cleaned = re.sub(r'^[0-9\.\-\s]+', '', cleaned)
    cleaned = re.sub(r'[\:\.\-]+$', '', cleaned).strip().upper()
    return cleaned, modifier.strip(), is_offscreen

def parse_screenplay_structure(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs full-document deterministic screenplay extraction:
    - Scenes (scene number, heading, location, time, page, lines, dialogue, participants)
    - Characters (speaking, non-speaking, mentions, aliases, dialogues, first/last appearance)
    - Story timeline and act milestones
    """
    scenes = []
    current_scene = None
    scene_counter = 0

    # Character trackers
    speaking_records: Dict[str, Dict[str, Any]] = {}
    present_records: Dict[str, Set[int]] = {}
    mentioned_records: Dict[str, Set[int]] = {}

    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["text"]
        lines = text.split("\n")

        for line_idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                continue

            # Check if this line is a scene heading
            heading_match = SCENE_HEADING_REGEX.match(line)
            if heading_match and not line.isupper() and len(line) < 120:
                pass
            if heading_match or (any(line.upper().startswith(p) for p in ["INT. ", "EXT. ", "INT/EXT ", "EXT/INT "]) and len(line) < 120):
                scene_counter += 1
                int_ext = "INT/EXT"
                location = "UNKNOWN"
                time_of_day = "UNKNOWN"

                if heading_match:
                    int_ext = heading_match.group(1).upper().replace(".", "")
                    location = heading_match.group(2).strip().upper()
                    time_of_day = heading_match.group(3).strip().upper()
                else:
                    parts = line.split("-")
                    int_ext = line[:8].split()[0].upper().replace(".", "")
                    location = parts[0][len(int_ext):].strip().upper()
                    if len(parts) > 1:
                        time_of_day = parts[-1].strip().upper()

                if current_scene:
                    scenes.append(current_scene)

                current_scene = {
                    "scene_number": scene_counter,
                    "heading": line,
                    "int_ext": int_ext,
                    "location": location,
                    "time_of_day": time_of_day,
                    "page": page_num,
                    "action_lines": [],
                    "dialogues": [],
                    "characters_present": set(),
                    "characters_speaking": set()
                }
                continue

            # Check character cue:
            # Typically centered or indented, all uppercase, short line (< 35 chars)
            line_upper = line.upper()
            is_potential_char = (
                line.isupper()
                and len(line) < 40
                and not line.endswith((".", "!", "?"))
                and not any(line.startswith(nw) for nw in NON_CHARACTER_WORDS)
                and not SCENE_HEADING_REGEX.match(line)
                and not any(line.startswith(p) for p in ["INT.", "EXT.", "INT/EXT", "EXT/INT"])
            )

            # If there's dialogue following this line
            if is_potential_char and line_idx + 1 < len(lines):
                next_line = lines[line_idx + 1].strip()
                if next_line and not next_line.isupper():
                    # This is confirmed dialogue cue
                    clean_name, modifier, is_offscreen = clean_character_name(line)
                    if len(clean_name) >= 2 and not clean_name.isdigit():
                        if clean_name not in speaking_records:
                            speaking_records[clean_name] = {
                                "canonical_name": clean_name,
                                "aliases": set(),
                                "first_page": page_num,
                                "speaking_pages": set(),
                                "dialogue_count": 0,
                                "is_unnamed_role": any(rk in clean_name for rk in ROLE_KEYWORDS),
                                "sample_dialogue": next_line[:150]
                            }
                        speaking_records[clean_name]["speaking_pages"].add(page_num)
                        speaking_records[clean_name]["dialogue_count"] += 1

                        if current_scene:
                            current_scene["characters_speaking"].add(clean_name)
                            current_scene["characters_present"].add(clean_name)
                            current_scene["dialogues"].append({
                                "character": clean_name,
                                "modifier": modifier,
                                "text": next_line,
                                "page": page_num
                            })
                        continue

            # Action narration line
            if current_scene:
                current_scene["action_lines"].append(line)
                # Check for character appearances in uppercase inside action text:
                # E.g. "COOPER enters the cockpit..."
                words = re.findall(r'\b[A-Z]{3,20}\b', line)
                for w in words:
                    if w not in NON_CHARACTER_WORDS and w in speaking_records:
                        current_scene["characters_present"].add(w)
                        if w not in present_records:
                            present_records[w] = set()
                        present_records[w].add(page_num)

    if current_scene:
        scenes.append(current_scene)

    # Alias normalization & deduplication (e.g. COOPER and COOP, PROFESSOR BRAND and BRAND)
    normalized_speaking: Dict[str, Dict[str, Any]] = {}
    names_by_length = sorted(list(speaking_records.keys()), key=len, reverse=True)

    for name in names_by_length:
        record = speaking_records[name]
        merged = False
        # Check if this name is an alias of an existing canonical character
        for canon_name, canon_record in normalized_speaking.items():
            # Matches: "COOP" in "COOPER", or "PROFESSOR BRAND" vs "BRAND"
            name_parts = set(name.split())
            canon_parts = set(canon_name.split())
            if (
                (name in canon_name and len(name) >= 4)
                or (canon_name in name and len(canon_name) >= 4)
                or (name_parts and name_parts.issubset(canon_parts))
                or (canon_parts and canon_parts.issubset(name_parts))
            ):
                canon_record["aliases"].add(name)
                canon_record["aliases"].update(record["aliases"])
                canon_record["speaking_pages"].update(record["speaking_pages"])
                canon_record["dialogue_count"] += record["dialogue_count"]
                if record["first_page"] < canon_record["first_page"]:
                    canon_record["first_page"] = record["first_page"]
                merged = True
                break

        if not merged:
            normalized_speaking[name] = record

    # Classify character tiers
    named_speaking = []
    unnamed_speaking = []
    for name, data in normalized_speaking.items():
        data["aliases"] = sorted(list(data["aliases"]))
        data["speaking_pages"] = sorted(list(data["speaking_pages"]))
        if data["is_unnamed_role"]:
            unnamed_speaking.append(data)
        else:
            named_speaking.append(data)

    # Convert sets in scenes to lists for JSON serialization
    for sc in scenes:
        sc["characters_present"] = sorted(list(sc["characters_present"]))
        sc["characters_speaking"] = sorted(list(sc["characters_speaking"]))

    return {
        "total_pages": len(pages),
        "total_scenes": len(scenes),
        "scenes": scenes,
        "named_speaking_characters": sorted(named_speaking, key=lambda x: x["dialogue_count"], reverse=True),
        "unnamed_speaking_roles": sorted(unnamed_speaking, key=lambda x: x["dialogue_count"], reverse=True),
        "total_named_speaking": len(named_speaking),
        "total_unnamed_speaking": len(unnamed_speaking),
        "total_distinct_speaking": len(named_speaking) + len(unnamed_speaking)
    }

