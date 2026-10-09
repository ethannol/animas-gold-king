"""Unit and name reconciliation for Water Quality Portal records.

Every conversion is an explicit written factor. Unknown units raise rather than
pass through silently; the caller logs the rows it excludes.
"""

from __future__ import annotations

# Canonical constituent names keyed by WQP CharacteristicName.
CHARACTERISTICS: dict[str, str] = {
    "Zinc": "zinc",
    "Copper": "copper",
    "Lead": "lead",
    "Cadmium": "cadmium",
    "Iron": "iron",
    "Manganese": "manganese",
    "Aluminum": "aluminium",
    "Arsenic": "arsenic",
    "pH": "ph",
    "Specific conductance": "spec_cond",
    "Flow": "flow",
    "Stream flow, instantaneous": "flow",
    "Flow rate, instantaneous": "flow",
}
METALS = ["zinc", "copper", "lead", "cadmium", "iron", "manganese", "aluminium", "arsenic"]

# Canonical units per constituent family.
CANONICAL_UNIT = {**{m: "ug/L" for m in METALS}, "ph": "pH units", "spec_cond": "uS/cm", "flow": "ft3/s"}

# Multiplicative factors to the canonical unit. Keys are the raw unit strings as the
# portal spells them (case preserved on purpose; both spellings occur).
METAL_FACTOR: dict[str, float] = {"ug/l": 1.0, "ug/L": 1.0, "mg/l": 1000.0, "mg/L": 1000.0}
SC_FACTOR: dict[str, float] = {"uS/cm": 1.0, "umho/cm": 1.0, "uS/cm @25C": 1.0, "mS/cm": 1000.0}
PH_UNITS = {"std units", "None", ""}
FLOW_FACTOR: dict[str, float] = {"ft3/sec": 1.0, "ft3/s": 1.0, "cfs": 1.0}

# Sample-fraction labels. "Recoverable"/"Total Recoverable" is the USGS and WQX wording for
# a whole-water (unfiltered) digestion; it is grouped with "Total" but the raw label is kept
# so the report can say which definitions were pooled.
DISSOLVED_LABELS = {"Dissolved", "Filtered, lab", "Filtered, field"}
TOTAL_LABELS = {"Total", "Total Recoverable", "Total Recovrble", "Recoverable"}


class UnitError(ValueError):
    pass


def factor_to_canonical(constituent: str, unit: str) -> float:
    """Factor that converts `unit` to the canonical unit for `constituent`."""
    if constituent in METALS:
        table = METAL_FACTOR
    elif constituent == "spec_cond":
        table = SC_FACTOR
    elif constituent == "flow":
        table = FLOW_FACTOR
    elif constituent == "ph":
        if unit in PH_UNITS:
            return 1.0
        raise UnitError(f"unexpected pH unit {unit!r}")
    else:
        raise UnitError(f"unknown constituent {constituent!r}")
    if unit not in table:
        raise UnitError(f"no conversion for {constituent} in unit {unit!r}")
    return table[unit]


def fraction_class(label: str, constituent: str) -> str:
    """'dissolved', 'total', 'na' (field parameters) or 'unknown'."""
    if constituent in ("ph", "spec_cond", "flow"):
        return "na"
    if label in DISSOLVED_LABELS:
        return "dissolved"
    if label in TOTAL_LABELS:
        return "total"
    return "unknown"
