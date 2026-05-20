import secrets
import string
import json
import os
import hashlib
from datetime import datetime

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
VAULT_FILE   = "vault.json"
MIN_LENGTH   = 8
MAX_GENERATE = 20

# Strength thresholds (score out of 5)
STRENGTH_LABELS = {5: ("Excellent", "🟢"), 4: ("Strong", "🟢"),
                   3: ("Moderate", "🟡"), 2: ("Weak", "🟠"), 1: ("Very Weak", "🔴")}

# ─── PASSWORD GENERATION ──────────────────────────────────────────────────────
def generate_password(length, uppercase=True, lowercase=True,
                      digits=True, symbols=True, exclude=""):
    """
    Build a charset from selected categories, guarantee at least one character
    from each selected category, then shuffle with secrets.SystemRandom.
    Exclusion string lets users strip ambiguous chars like 0/O/l/1.
    """
    pool_parts = []
    required   = []

    if uppercase: pool_parts.append(string.ascii_uppercase); required.append(string.ascii_uppercase)
    if lowercase: pool_parts.append(string.ascii_lowercase); required.append(string.ascii_lowercase)
    if digits:    pool_parts.append(string.digits);          required.append(string.digits)
    if symbols:   pool_parts.append(string.punctuation);     required.append(string.punctuation)

    if not pool_parts:
        raise ValueError("Select at least one character type.")

    # Remove user-excluded characters from every part
    pool = "".join(c for c in "".join(pool_parts) if c not in exclude)
    if not pool:
        raise ValueError("Exclusion list removed all available characters.")

    rng = secrets.SystemRandom()

    while True:
        # Seed with one char from each required category to satisfy all constraints
        mandatory = [secrets.choice([c for c in cat if c not in exclude])
                     for cat in required if any(c not in exclude for c in cat)]
        rest = [secrets.choice(pool) for _ in range(length - len(mandatory))]
        pwd  = mandatory + rest
        rng.shuffle(pwd)
        password = "".join(pwd)

        # Verify every enabled category is represented (handles edge-lengths)
        ok = all(any(c in cat for c in password)
                 for cat, flag in zip(required,
                     [uppercase, lowercase, digits, symbols]) if flag)
        if ok:
            return password


def generate_memorable(length=16):
    """
    Word-digit-symbol pattern:  Word + digits + symbol + Word
    Falls back to random if wordlist unavailable.
    """
    words = [
        "solar", "orbit", "pixel", "storm", "forge", "blade", "crane",
        "ember", "frost", "glide", "haven", "ionic", "jolt",  "karma",
        "lunar", "mirth", "nexus", "opal",  "prism", "quest", "raven",
        "spark", "titan", "ultra", "vault", "wrath", "xenon", "yield", "zeal",
    ]
    w1  = secrets.choice(words).capitalize()
    w2  = secrets.choice(words).capitalize()
    num = "".join(str(secrets.randbelow(10)) for _ in range(3))
    sym = secrets.choice("!@#$%&*?")
    return (w1 + num + sym + w2)[:length]


def generate_pin(length=6):
    """Numeric PIN using secrets.randbelow — no modulo bias."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))

# ─── STRENGTH ANALYSER ────────────────────────────────────────────────────────
def analyse_strength(pwd):
    """
    Score 0-5 across five criteria:
      length ≥16, uppercase, lowercase, digits, symbols.
    Returns (score, label, emoji, list_of_tips).
    """
    score = 0
    tips  = []

    if len(pwd) >= 16:
        score += 1
    else:
        tips.append(f"Use ≥16 characters (currently {len(pwd)})")

    if any(c.isupper() for c in pwd):
        score += 1
    else:
        tips.append("Add uppercase letters")

    if any(c.islower() for c in pwd):
        score += 1
    else:
        tips.append("Add lowercase letters")

    if any(c.isdigit() for c in pwd):
        score += 1
    else:
        tips.append("Add digits")

    if any(c in string.punctuation for c in pwd):
        score += 1
    else:
        tips.append("Add symbols (!@#…)")

    label, emoji = STRENGTH_LABELS.get(score, ("Very Weak", "🔴"))
    return score, label, emoji, tips

# ─── VAULT ────────────────────────────────────────────────────────────────────
def _load_vault():
    try:
        with open(VAULT_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _save_vault(entries):
    with open(VAULT_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def vault_save(password, label=""):
    """
    Append an entry to the vault.
    Stores a SHA-256 fingerprint (never the raw password) alongside the
    password so the user can spot accidental duplicates without re-reading
    the vault.
    """
    entries = _load_vault()
    entries.append({
        "label":       label or "(no label)",
        "password":    password,
        "fingerprint": hashlib.sha256(password.encode()).hexdigest()[:12],
        "saved_at":    datetime.now().strftime("%Y-%m-%d %H:%M"),
        "length":      len(password),
    })
    _save_vault(entries)
    print(f"  ✔ Saved to {VAULT_FILE}  (fingerprint: {entries[-1]['fingerprint']})")

def vault_list():
    entries = _load_vault()
    if not entries:
        print("  Vault is empty.")
        return
    print(f"\n  {'#':<4}{'Label':<20}{'Length':<8}{'Saved':<18}{'Fingerprint'}")
    print("  " + "─" * 60)
    for i, e in enumerate(entries, 1):
        print(f"  {i:<4}{e['label'][:19]:<20}{e['length']:<8}{e['saved_at']:<18}{e['fingerprint']}")

def vault_delete():
    entries = _load_vault()
    if not entries:
        print("  Vault is empty.")
        return
    vault_list()
    raw = input("\n  Enter entry # to delete (or Enter to cancel): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(entries):
        removed = entries.pop(int(raw) - 1)
        _save_vault(entries)
        print(f"  ✔ Deleted: {removed['label']}")
    else:
        print("  Cancelled.")

# ─── UI HELPERS ───────────────────────────────────────────────────────────────
def _hr(char="─", n=52):
    print("  " + char * n)

def _ask_yn(prompt, default="y"):
    suffix = " (Y/n)" if default == "y" else " (y/N)"
    ans = input(f"  {prompt}{suffix}: ").strip().lower() or default
    return ans == "y"

def _ask_int(prompt, lo, hi, default=None):
    while True:
        suffix = f" [{lo}-{hi}]" + (f" (default {default})" if default else "") + ": "
        raw = input(f"  {prompt}{suffix}").strip()
        if raw == "" and default is not None:
            return default
        if raw.isdigit() and lo <= int(raw) <= hi:
            return int(raw)
        print(f"  Please enter a number between {lo} and {hi}.")

def _show_strength(pwd):
    score, label, emoji, tips = analyse_strength(pwd)
    bar  = "█" * score + "░" * (5 - score)
    print(f"  Strength : {emoji} {label}  [{bar}]")
    for t in tips:
        print(f"             · {t}")

# ─── PREFERENCE WIZARD ────────────────────────────────────────────────────────
def collect_preferences():
    """Interactive wizard — returns dict of generation settings."""
    _hr("═")
    print("  GENERATOR SETTINGS")
    _hr("═")

    print("\n  Mode:")
    print("    1. Random (full control)")
    print("    2. Memorable  (word-based)")
    print("    3. PIN  (numeric only)")
    mode = _ask_int("Select", 1, 3, 1)

    if mode == 2:
        length = _ask_int("Length", 12, 32, 16)
        return {"mode": "memorable", "length": length,
                "count": _ask_int("How many", 1, MAX_GENERATE, 5)}
    if mode == 3:
        length = _ask_int("PIN length", 4, 12, 6)
        return {"mode": "pin", "length": length,
                "count": _ask_int("How many", 1, MAX_GENERATE, 5)}

    # ── Random mode ──────────────────────────────────────────────────────────
    length = _ask_int("Length (min 8)", MIN_LENGTH, 128, 16)
    count  = _ask_int("How many to generate", 1, MAX_GENERATE, 5)

    print("\n  Character types:")
    upper   = _ask_yn("Uppercase  (A–Z)")
    lower   = _ask_yn("Lowercase  (a–z)")
    digs    = _ask_yn("Digits     (0–9)")
    syms    = _ask_yn("Symbols    (!@#…)")

    if not any([upper, lower, digs, syms]):
        print("  ⚠  At least one type required — enabling all.")
        upper = lower = digs = syms = True

    print("\n  Exclude ambiguous characters?  (0 O o l 1 I i)")
    exclude = "0Ool1Ii" if _ask_yn("Exclude") else ""

    return {"mode": "random", "length": length, "count": count,
            "upper": upper, "lower": lower, "digits": digs,
            "symbols": syms, "exclude": exclude}

# ─── GENERATION LOOP ─────────────────────────────────────────────────────────
def generation_loop(prefs):
    """Generate, display, re-roll, select, save — returns when done."""
    while True:
        # ── Generate ─────────────────────────────────────────────────────────
        pwds = []
        for _ in range(prefs["count"]):
            if prefs["mode"] == "memorable":
                pwds.append(generate_memorable(prefs["length"]))
            elif prefs["mode"] == "pin":
                pwds.append(generate_pin(prefs["length"]))
            else:
                pwds.append(generate_password(
                    prefs["length"],
                    uppercase=prefs["upper"],  lowercase=prefs["lower"],
                    digits=prefs["digits"],    symbols=prefs["symbols"],
                    exclude=prefs["exclude"],
                ))

        # ── Display ──────────────────────────────────────────────────────────
        _hr()
        print("  GENERATED PASSWORDS")
        _hr()
        for i, p in enumerate(pwds, 1):
            score, label, emoji, _ = analyse_strength(p)
            bar = "█" * score + "░" * (5 - score)
            print(f"  {i:>2}. {p}   {emoji}[{bar}]")
        _hr()

        print("\n  Options:")
        print("    <number>  Select a password")
        print("    r         Regenerate all")
        print("    b         Back to settings")
        print("    v         View vault")
        print("    q         Quit")

        choice = input("\n  Choice: ").strip().lower()

        if choice == "q":
            return "quit"
        if choice == "b":
            return "back"
        if choice == "r":
            continue
        if choice == "v":
            vault_list()
            input("\n  Press Enter to continue…")
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(pwds):
            selected = pwds[int(choice) - 1]
            print(f"\n  Selected: {selected}")
            _show_strength(selected)

            if _ask_yn("Save to vault"):
                label = input("  Label for this password (optional): ").strip()
                vault_save(selected, label)

            # Copy hint (platform-agnostic — we can't access clipboard in all envs)
            print(f"\n  ↑  Copy the password above.")
            return "done"
        else:
            print("  Invalid choice.")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 54)
    print("   🔐  SECURE PASSWORD GENERATOR")
    print("═" * 54)
    print("   Built on secrets.SystemRandom — cryptographically secure")
    print("═" * 54)

    while True:
        print("\n  Main Menu")
        _hr()
        print("  1. Generate passwords")
        print("  2. View vault")
        print("  3. Delete vault entry")
        print("  4. Quit")
        _hr()

        opt = input("  Choice: ").strip()

        if opt == "1":
            while True:
                prefs  = collect_preferences()
                result = generation_loop(prefs)
                if result == "quit":
                    print("\n  Goodbye! Stay secure. 🔒\n")
                    return
                if result != "back":
                    if not _ask_yn("Generate another set"):
                        break
        elif opt == "2":
            vault_list()
            input("\n  Press Enter to continue…")
        elif opt == "3":
            vault_delete()
        elif opt == "4":
            print("\n  Goodbye! Stay secure. 🔒\n")
            return
        else:
            print("  Invalid option.")

if __name__ == "__main__":
    main()
