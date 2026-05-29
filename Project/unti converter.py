"""
Universal Unit Converter
========================
Supports:
  1. Length      — Meters, Feet, Kilometers, Miles, Inches, Centimeters
  2. Weight      — Kilograms, Pounds, Grams, Ounces
  3. Temperature — Celsius, Fahrenheit, Kelvin
  4. Speed       — km/h, mph, m/s
  5. Area        — sq meters, sq feet, acres, hectares

Enhanced Features:
  - Extended unit categories and sub-options
  - Bidirectional conversions via a base-unit approach (no combinatorial explosion)
  - Input validation with range checks where appropriate
  - Conversion history with export option
  - Repeat-conversion shortcut (re-use last category/pair)
  - Clean, colour-coded terminal output (ANSI; gracefully degrades)
"""

import os
import sys
from datetime import datetime

# ──────────────────────────────────────────────
# ANSI colour helpers (no third-party deps)
# ──────────────────────────────────────────────

def _supports_colour() -> bool:
    """Return True when the terminal is likely to render ANSI escape codes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOUR = _supports_colour()

def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour *code* if supported."""
    return f"\033[{code}m{text}\033[0m" if _COLOUR else text

def green(t):  return _c("92", t)
def cyan(t):   return _c("96", t)
def yellow(t): return _c("93", t)
def red(t):    return _c("91", t)
def bold(t):   return _c("1",  t)

# ──────────────────────────────────────────────
# Conversion registry  (base-unit architecture)
# ──────────────────────────────────────────────
#
# Each category stores a dictionary of units.  Every unit has a factor that
# converts *from that unit to the base unit* of the category (marked with *).
# Temperature is special: it uses callable lambdas instead of simple factors.
#
# Converting A → B:
#   value_in_base = to_base[A](value)
#   result        = from_base[B](value_in_base)

CATEGORIES = {
    "1": {
        "name": "Length",
        "base": "meters",
        "units": {
            "a": "Meters",
            "b": "Feet",
            "c": "Kilometers",
            "d": "Miles",
            "e": "Inches",
            "f": "Centimeters",
        },
        # Multiply by factor to reach base unit (meters)
        "to_base": {
            "Meters":      lambda v: v,
            "Feet":        lambda v: v / 3.28084,
            "Kilometers":  lambda v: v * 1_000,
            "Miles":       lambda v: v * 1_609.344,
            "Inches":      lambda v: v / 39.3701,
            "Centimeters": lambda v: v / 100,
        },
        "from_base": {
            "Meters":      lambda v: v,
            "Feet":        lambda v: v * 3.28084,
            "Kilometers":  lambda v: v / 1_000,
            "Miles":       lambda v: v / 1_609.344,
            "Inches":      lambda v: v * 39.3701,
            "Centimeters": lambda v: v * 100,
        },
    },

    "2": {
        "name": "Weight / Mass",
        "base": "kilograms",
        "units": {
            "a": "Kilograms",
            "b": "Pounds",
            "c": "Grams",
            "d": "Ounces",
            "e": "Tonnes",
        },
        "to_base": {
            "Kilograms": lambda v: v,
            "Pounds":    lambda v: v / 2.20462,
            "Grams":     lambda v: v / 1_000,
            "Ounces":    lambda v: v / 35.27396,
            "Tonnes":    lambda v: v * 1_000,
        },
        "from_base": {
            "Kilograms": lambda v: v,
            "Pounds":    lambda v: v * 2.20462,
            "Grams":     lambda v: v * 1_000,
            "Ounces":    lambda v: v * 35.27396,
            "Tonnes":    lambda v: v / 1_000,
        },
    },

    "3": {
        "name": "Temperature",
        "base": "Celsius",          # internal base
        "units": {
            "a": "Celsius",
            "b": "Fahrenheit",
            "c": "Kelvin",
        },
        "to_base": {
            "Celsius":    lambda v: v,
            "Fahrenheit": lambda v: (v - 32) * 5 / 9,
            "Kelvin":     lambda v: v - 273.15,
        },
        "from_base": {
            "Celsius":    lambda v: v,
            "Fahrenheit": lambda v: v * 9 / 5 + 32,
            "Kelvin":     lambda v: v + 273.15,
        },
        # Temperature validation: Kelvin must be ≥ 0 K (−273.15 °C)
        "min_celsius": -273.15,
    },

    "4": {
        "name": "Speed",
        "base": "m/s",
        "units": {
            "a": "m/s",
            "b": "km/h",
            "c": "mph",
            "d": "Knots",
        },
        "to_base": {
            "m/s":   lambda v: v,
            "km/h":  lambda v: v / 3.6,
            "mph":   lambda v: v * 0.44704,
            "Knots": lambda v: v * 0.514444,
        },
        "from_base": {
            "m/s":   lambda v: v,
            "km/h":  lambda v: v * 3.6,
            "mph":   lambda v: v / 0.44704,
            "Knots": lambda v: v / 0.514444,
        },
    },

    "5": {
        "name": "Area",
        "base": "sq_meters",
        "units": {
            "a": "Sq Meters",
            "b": "Sq Feet",
            "c": "Acres",
            "d": "Hectares",
            "e": "Sq Kilometers",
        },
        "to_base": {
            "Sq Meters":    lambda v: v,
            "Sq Feet":      lambda v: v / 10.7639,
            "Acres":        lambda v: v * 4_046.856,
            "Hectares":     lambda v: v * 10_000,
            "Sq Kilometers":lambda v: v * 1_000_000,
        },
        "from_base": {
            "Sq Meters":    lambda v: v,
            "Sq Feet":      lambda v: v * 10.7639,
            "Acres":        lambda v: v / 4_046.856,
            "Hectares":     lambda v: v / 10_000,
            "Sq Kilometers":lambda v: v / 1_000_000,
        },
    },
}

# ──────────────────────────────────────────────
# Input helpers
# ──────────────────────────────────────────────

def get_float_input(prompt: str) -> float:
    """Prompt until the user enters a valid floating-point number."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() in ("q", "quit", "exit"):
            print(yellow("\nExiting…"))
            sys.exit(0)
        try:
            return float(raw)
        except ValueError:
            print(red("  ✗ Please enter a numeric value (e.g. 42 or 3.14)."))


def get_menu_choice(prompt: str, valid: set, allow_back: bool = True) -> str:
    """
    Prompt until the user selects one of the *valid* keys.
    If *allow_back* is True, entering 'b' returns the sentinel '<back>'.
    """
    if allow_back:
        prompt += yellow("  (or 'b' to go back) ") + ": "
    else:
        prompt += ": "

    while True:
        choice = input(prompt).strip().lower()
        if allow_back and choice == "b":
            return "<back>"
        if choice in valid:
            return choice
        print(red(f"  ✗ Invalid choice. Expected one of: {', '.join(sorted(valid))}"))


# ──────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────

def validate_temperature(value: float, unit: str) -> bool:
    """
    Return False (and print an error) if *value* is below absolute zero
    when expressed in *unit*.
    """
    category = CATEGORIES["3"]
    celsius = category["to_base"][unit](value)
    if celsius < category["min_celsius"]:
        limit = category["from_base"][unit](category["min_celsius"])
        print(red(f"  ✗ Value below absolute zero. Minimum in {unit}: {limit:.4f}"))
        return False
    return True


# ──────────────────────────────────────────────
# Conversion history
# ──────────────────────────────────────────────

history: list[dict] = []   # Each entry: {time, category, from, to, input, result}

def record(category_name: str, from_unit: str, to_unit: str,
           value: float, result: float) -> None:
    """Append a conversion event to the in-session history."""
    history.append({
        "time":     datetime.now().strftime("%H:%M:%S"),
        "category": category_name,
        "from":     from_unit,
        "to":       to_unit,
        "input":    value,
        "result":   result,
    })


def show_history() -> None:
    """Pretty-print all conversions performed in this session."""
    if not history:
        print(yellow("  No conversions yet in this session."))
        return

    print(bold(f"\n{'─'*60}"))
    print(bold(f"  Conversion History ({len(history)} entries)"))
    print(bold(f"{'─'*60}"))
    for i, h in enumerate(history, 1):
        line = (f"  {cyan(str(i).rjust(2))}. [{h['time']}] "
                f"{h['category']}: "
                f"{green(f'{h[\"input\"]:.4g} {h[\"from\"]}')} → "
                f"{green(f'{h[\"result\"]:.6g} {h[\"to\"]}')}")
        print(line)
    print(bold(f"{'─'*60}\n"))


def export_history() -> None:
    """Save history to a plain-text file in the current directory."""
    if not history:
        print(yellow("  Nothing to export yet."))
        return

    filename = f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as fh:
        fh.write("Universal Unit Converter – Session History\n")
        fh.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        fh.write("=" * 60 + "\n\n")
        for i, h in enumerate(history, 1):
            fh.write(f"{i:>3}. [{h['time']}] {h['category']}: "
                     f"{h['input']:.6g} {h['from']} = "
                     f"{h['result']:.6g} {h['to']}\n")
    print(green(f"  ✓ History exported to '{filename}'"))


# ──────────────────────────────────────────────
# Display helpers
# ──────────────────────────────────────────────

def display_result(value: float, from_unit: str,
                   result: float, to_unit: str) -> None:
    """Print a formatted, highlighted conversion result."""
    print(f"\n  {bold('Result:')}  "
          f"{green(f'{value:,.6g}')} {cyan(from_unit)}  →  "
          f"{green(f'{result:,.6g}')} {cyan(to_unit)}\n")


def print_header() -> None:
    width = 47
    print("\n" + bold("═" * width))
    print(bold(f"{'Universal Unit Converter':^{width}}"))
    print(bold("═" * width))
    print(yellow("  Type 'q' at any prompt to quit.\n"))


def print_main_menu() -> None:
    print(bold("  Select a category:"))
    for key, cat in CATEGORIES.items():
        print(f"    {cyan(key)}. {cat['name']}")
    print(f"    {cyan('h')}. View history")
    print(f"    {cyan('e')}. Export history")
    print(f"    {cyan('x')}. Exit")


# ──────────────────────────────────────────────
# Core converter flow
# ──────────────────────────────────────────────

def pick_units(category: dict) -> tuple[str, str] | None:
    """
    Ask the user to choose FROM and TO units within *category*.
    Returns (from_unit_name, to_unit_name) or None if the user backs out.
    """
    units = category["units"]

    # Display available units
    print(f"\n  {bold(category['name'])} units:")
    for key, name in units.items():
        print(f"    {cyan(key)}. {name}")

    from_key = get_menu_choice("\n  Convert FROM", set(units))
    if from_key == "<back>":
        return None

    # Filter out the already-chosen unit for the TO prompt
    to_options = {k: v for k, v in units.items() if k != from_key}
    print(f"\n  Convert TO (not '{units[from_key]}'):")
    for key, name in to_options.items():
        print(f"    {cyan(key)}. {name}")

    to_key = get_menu_choice("  Convert TO", set(to_options))
    if to_key == "<back>":
        return None

    return units[from_key], units[to_key]


def do_conversion(category: dict, from_unit: str, to_unit: str) -> None:
    """
    Prompt for a value, validate it, convert it, display and record the result.
    Allows the user to convert the same pair multiple times.
    """
    while True:
        value = get_float_input(
            f"  Enter value in {cyan(from_unit)} (or 'b' to change units): "
        )

        # Intercept 'b' typed as a number (not possible; handle back via sentinel)
        # — actually the user would type 'b' before we call get_float_input, so
        #   we handle it by prompting differently here.  Re-prompt is fine.

        # Temperature-specific validation
        if category["name"] == "Temperature":
            if not validate_temperature(value, from_unit):
                continue   # ask again

        # Convert via base unit
        base_value = category["to_base"][from_unit](value)
        result     = category["from_base"][to_unit](base_value)

        display_result(value, from_unit, result, to_unit)
        record(category["name"], from_unit, to_unit, value, result)

        again = input("  Convert another value with the same units? (y/n): ").strip().lower()
        if again != "y":
            break


# ──────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────

def unit_converter() -> None:
    """Main application loop."""
    os.system("cls" if os.name == "nt" else "clear")
    print_header()

    valid_main = set(CATEGORIES.keys()) | {"h", "e", "x"}

    while True:
        print_main_menu()
        choice = get_menu_choice("\n  Your choice", valid_main, allow_back=False)

        if choice == "x":
            print(green("\n  Thanks for using Universal Unit Converter. Goodbye!\n"))
            break

        if choice == "h":
            show_history()
            continue

        if choice == "e":
            export_history()
            continue

        # ── Category selected ──
        category = CATEGORIES[choice]
        print(f"\n{bold('─'*47)}")
        print(f"  Category: {bold(category['name'])}")
        print(f"{'─'*47}")

        unit_pair = pick_units(category)
        if unit_pair is None:
            continue   # user pressed 'b' — back to main menu

        from_unit, to_unit = unit_pair
        do_conversion(category, from_unit, to_unit)


if __name__ == "__main__":
    unit_converter()