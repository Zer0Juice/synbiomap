"""
compare_geocoding_llms.py — benchmark Ollama (qwen2.5:3b) vs Claude Haiku
for extracting city names from iGEM institution names.

Uses the same prompt format as geocode_igem_teams.py (Tier 3).
Prints accuracy, per-item results, and timing for each model.

Usage:
    ANTHROPIC_API_KEY=sk-... python scripts/compare_geocoding_llms.py

Requires:
    pip install anthropic ollama
"""

import json
import os
import re
import time
from pathlib import Path

# Load .env from repo root so ANTHROPIC_API_KEY is available without export
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ---------------------------------------------------------------------------
# Test cases: (institution, team_name, iso3, expected_city)
# A mix of easy (full names), medium (common abbreviations), and hard
# (department-only names that need team-name context to resolve).
# ---------------------------------------------------------------------------

TEST_CASES = [
    # Easy — full university names
    ("Massachusetts Institute of Technology", "MIT_MAHE",    "USA", "Cambridge"),
    ("University of Cambridge",               "Cambridge-JIC","GBR", "Cambridge"),
    ("ETH Zurich",                            "ETH_Zurich",   "CHE", "Zurich"),
    ("Peking University",                     "Peking",       "CHN", "Beijing"),
    ("University of Tokyo",                   "Tokyo",        "JPN", "Tokyo"),

    # Medium — common abbreviations
    ("KAIST",                                 "KAIST",        "KOR", "Daejeon"),
    ("BUCT",                                  "BUCT",         "CHN", "Beijing"),
    ("ECUST",                                 "ECUST",        "CHN", "Shanghai"),
    ("HKUST",                                 "HKUST",        "CHN", "Hong Kong"),
    ("IIT Delhi",                             "IIT-Delhi",    "IND", "New Delhi"),

    # Medium — informal or abbreviated names
    ("Osaka Univ.",                           "Osaka",        "JPN", "Osaka"),
    ("TU Delft",                              "TUDelft",      "NLD", "Delft"),
    ("Uppsala Univ.",                         "Uppsala",      "SWE", "Uppsala"),
    ("Technion",                              "Technion-IL",  "ISR", "Haifa"),
    ("INSA Lyon",                             "INSA-Lyon",    "FRA", "Lyon"),

    # Hard — department names that need team-name context
    ("Department of Microbiology",            "CBNU-Korea",   "KOR", "Cheongju"),
    ("Department of Biology",                 "NJU-China",    "CHN", "Nanjing"),
    ("School of Life Sciences",               "Fudan",        "CHN", "Shanghai"),
    ("Faculty of Engineering",                "Lund",         "SWE", "Lund"),
    ("College of Sciences",                   "WHU-China",    "CHN", "Wuhan"),
]

BATCH_PROMPT_TEMPLATE = (
    "You are a geocoding assistant. For each entry below, use both the "
    "institution name AND the team name as clues to identify the city "
    "the institution is located in.\n"
    "Reply ONLY with a valid JSON array — no explanation, no markdown.\n"
    'Each element: {{"city": "...", "country": "..."}}\n'
    "If you are unsure, make your best guess.\n\n"
    "Entries:\n{lines}"
)


def build_lines(cases):
    return "\n".join(
        f'{i+1}. Institution: "{inst}" | Team name: "{team}" | Country ISO3: {iso3}'
        for i, (inst, team, iso3, _) in enumerate(cases)
    )


def _unwrap(item):
    while isinstance(item, list):
        item = item[0] if item else {}
    return item if isinstance(item, dict) else {}


def parse_response(raw: str) -> list[dict]:
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        return []
    try:
        parsed = json.loads(match.group(0))
        return [_unwrap(item) for item in parsed]
    except json.JSONDecodeError:
        return []


def score(predicted: str, expected: str) -> bool:
    """Case-insensitive substring match — accepts partial city names."""
    if not predicted:
        return False
    return (expected.lower() in predicted.lower() or
            predicted.lower() in expected.lower())


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------

def run_ollama(cases: list, model: str = "qwen2.5:3b") -> tuple[list[dict], float]:
    import ollama

    prompt = BATCH_PROMPT_TEMPLATE.format(lines=build_lines(cases))
    t0 = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    elapsed = time.time() - t0
    raw = response["message"]["content"].strip()
    return parse_response(raw), elapsed


# ---------------------------------------------------------------------------
# Claude Haiku
# ---------------------------------------------------------------------------

def run_haiku(cases: list, model: str = "claude-haiku-4-5-20251001") -> tuple[list[dict], float]:
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY environment variable first.")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = BATCH_PROMPT_TEMPLATE.format(lines=build_lines(cases))

    t0 = time.time()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - t0
    raw = message.content[0].text.strip()
    return parse_response(raw), elapsed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def evaluate(model_name: str, results: list[dict], elapsed: float):
    correct = 0
    print(f"\n{'='*60}")
    print(f"  {model_name}  ({elapsed:.1f}s for {len(TEST_CASES)} items, "
          f"{elapsed/len(TEST_CASES):.2f}s/item)")
    print(f"{'='*60}")
    print(f"  {'#':<3}  {'Expected':<14}  {'Got':<20}  {'OK?'}")
    print(f"  {'-'*3}  {'-'*14}  {'-'*20}  {'-'*4}")

    for i, (inst, team, iso3, expected) in enumerate(TEST_CASES):
        entry = results[i] if i < len(results) else {}
        predicted = entry.get("city", "")
        ok = score(predicted, expected)
        if ok:
            correct += 1
        marker = "✓" if ok else "✗"
        print(f"  {i+1:<3}  {expected:<14}  {predicted:<20}  {marker}")

    pct = 100 * correct / len(TEST_CASES)
    print(f"\n  Accuracy: {correct}/{len(TEST_CASES)} ({pct:.0f}%)")
    return correct


def main():
    print("Running Ollama (qwen2.5:3b)…")
    try:
        ollama_results, ollama_time = run_ollama(TEST_CASES)
    except Exception as e:
        print(f"  Ollama failed: {e}")
        ollama_results, ollama_time = [], 0.0

    print("Running Claude Haiku…")
    try:
        haiku_results, haiku_time = run_haiku(TEST_CASES)
    except Exception as e:
        print(f"  Haiku failed: {e}")
        haiku_results, haiku_time = [], 0.0

    ollama_score = evaluate("Ollama qwen2.5:3b", ollama_results, ollama_time)
    haiku_score  = evaluate("Claude Haiku 4.5",  haiku_results,  haiku_time)

    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"  Ollama qwen2.5:3b : {ollama_score}/{len(TEST_CASES)} correct")
    print(f"  Claude Haiku 4.5  : {haiku_score}/{len(TEST_CASES)} correct")
    if haiku_score > ollama_score:
        print("  → Haiku is more accurate for this task.")
    elif ollama_score > haiku_score:
        print("  → Ollama is more accurate for this task.")
    else:
        print("  → Both models scored the same.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
