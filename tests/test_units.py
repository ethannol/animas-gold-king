import pytest

from animas.units import UnitError, factor_to_canonical, fraction_class


def test_metal_units():
    assert factor_to_canonical("zinc", "ug/L") == 1.0
    assert factor_to_canonical("zinc", "ug/l") == 1.0
    assert factor_to_canonical("zinc", "mg/L") == 1000.0
    assert 2.5 * factor_to_canonical("copper", "mg/l") == 2500.0


def test_conductance_and_ph():
    assert factor_to_canonical("spec_cond", "umho/cm") == factor_to_canonical("spec_cond", "uS/cm") == 1.0
    assert factor_to_canonical("ph", "std units") == 1.0


def test_unknown_unit_raises():
    with pytest.raises(UnitError):
        factor_to_canonical("zinc", "mg/kg")
    with pytest.raises(UnitError):
        factor_to_canonical("ph", "ug/L")


def test_fraction_classes():
    assert fraction_class("Dissolved", "zinc") == "dissolved"
    assert fraction_class("Total Recoverable", "zinc") == "total"
    assert fraction_class("Recoverable", "iron") == "total"
    assert fraction_class("Suspended", "zinc") == "unknown"
    assert fraction_class("", "zinc") == "unknown"
    assert fraction_class("", "ph") == "na"
