"""Bounded whole-dollar compatibility of the extracted business-loss component.

YAML covers the policy examples. This differential test covers Core's float32
storage and ``adds`` accumulation, which YAML cannot compare with the former
single-formula calculation. The independent reference applies sections 461(l)
and 1211(b) to leaf inputs and casts the combined deduction only once, as the
pre-extraction formula did.

All intermediate totals stay below 2**24, the exact-integer range of float32.
This is a bounded guarantee, not parity for fractional dollars or larger totals.
Use production classes in one small Core system, without building or copying a
country model per case; package import constructs its global model once. This
module belongs to the existing rest-python core CI group.
"""

from pathlib import Path

import numpy as np
import pytest
import yaml
from policyengine_core.parameters import ParameterNode
from policyengine_core.parameters.config import Loader
from policyengine_core.simulations import Simulation
from policyengine_core.taxbenefitsystems import TaxBenefitSystem

import policyengine_us
from policyengine_us.entities import Person, TaxUnit
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.capital_losses_allowed_against_gains import (
    capital_losses_allowed_against_gains,
)
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.limited_business_loss import (
    limited_business_loss,
)
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.limited_capital_loss import (
    limited_capital_loss,
)
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.loss_ald import (
    loss_ald,
)
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
    filing_status,
)
from policyengine_us.variables.household.demographic.tax_unit.is_tax_unit_dependent import (
    is_tax_unit_dependent,
)
from policyengine_us.variables.household.income.person.capital_gains.capital_gains import (
    capital_gains,
)
from policyengine_us.variables.household.income.person.capital_gains.capital_losses import (
    capital_losses,
)
from policyengine_us.variables.household.income.person.capital_gains.long_term_capital_gains import (
    long_term_capital_gains,
)
from policyengine_us.variables.household.income.person.capital_gains.non_sch_d_capital_gains import (
    non_sch_d_capital_gains,
)
from policyengine_us.variables.household.income.person.capital_gains.other_net_gain import (
    other_net_gain,
)
from policyengine_us.variables.household.income.person.capital_gains.short_term_capital_gains import (
    short_term_capital_gains,
)
from policyengine_us.variables.household.income.person.estate.estate_income import (
    estate_income,
)
from policyengine_us.variables.household.income.person.farm.farm_operations_income import (
    farm_operations_income,
)
from policyengine_us.variables.household.income.person.farm.farm_rent_income import (
    farm_rent_income,
)
from policyengine_us.variables.household.income.person.misc.rental_income import (
    rental_income,
)
from policyengine_us.variables.household.income.person.self_employment.partnership_income import (
    partnership_income,
)
from policyengine_us.variables.household.income.person.self_employment.partnership_s_corp_income import (
    partnership_s_corp_income,
)
from policyengine_us.variables.household.income.person.self_employment.s_corp_income import (
    s_corp_income,
)
from policyengine_us.variables.household.income.person.self_employment.total_self_employment_income import (
    total_self_employment_income,
)
from policyengine_us.variables.input.self_employment_income import (
    self_employment_income,
)
from policyengine_us.variables.input.sstb_self_employment_income import (
    sstb_self_employment_income,
)

INPUT_CLASSES = (
    self_employment_income,
    sstb_self_employment_income,
    farm_operations_income,
    rental_income,
    farm_rent_income,
    estate_income,
    partnership_income,
    s_corp_income,
    short_term_capital_gains,
    long_term_capital_gains,
    non_sch_d_capital_gains,
)
INPUTS = tuple(variable.__name__ for variable in INPUT_CLASSES)
ZERO = dict.fromkeys(INPUTS, 0)
STATUSES = tuple(status.name for status in FilingStatus)
EXACT_INTEGER_LIMIT = 2**24


@pytest.fixture(scope="module")
def system():
    result = TaxBenefitSystem(entities=[Person, TaxUnit])
    result.add_variables(
        *INPUT_CLASSES,
        filing_status,
        is_tax_unit_dependent,
        other_net_gain,
        total_self_employment_income,
        partnership_s_corp_income,
        capital_gains,
        capital_losses,
        limited_business_loss,
        capital_losses_allowed_against_gains,
        limited_capital_loss,
        loss_ald,
    )
    parameter_root = Path(policyengine_us.__file__).parent / "parameters"

    def load(relative_path):
        return yaml.load((parameter_root / relative_path).read_text(), Loader=Loader)

    # Read only the published thresholds and gross-income source list needed
    # by these formulas; no full parameter-tree construction or copying.
    result.parameters = ParameterNode(
        "",
        data={
            "gov": {
                "irs": {
                    "ald": {
                        "loss": {
                            "max": load("gov/irs/ald/loss/max.yaml"),
                            "capital": {
                                "max": load("gov/irs/ald/loss/capital/max.yaml")
                            },
                        }
                    },
                    "gross_income": {
                        "sources": load("gov/irs/gross_income/sources.yaml")
                    },
                }
            }
        },
    )
    return result


def _draw_units(year, thresholds, capital_caps):
    rng = np.random.default_rng(9762 + year)
    units = []
    for i in range(120):
        members = []
        for dependent in [False] + ([False] if i % 2 else []) + [True] * (i % 3):
            amounts = {name: int(rng.integers(-100_000, 100_001)) for name in INPUTS}
            amounts["non_sch_d_capital_gains"] = abs(amounts["non_sch_d_capital_gains"])
            members.append((amounts, dependent))
        units.append(
            {
                "status": STATUSES[i % len(STATUSES)],
                "other": int(rng.integers(-100_000, 100_001)),
                "members": members,
            }
        )
    for status in STATUSES:
        for offset in (-1, 0, 1):
            # Below/at/above business and capital limits, including MFS.
            # Opposite-signed short/long-term sources net before the
            # distribution offsets the resulting loss.
            head = {
                **ZERO,
                "farm_rent_income": 12_345,
                "rental_income": -(thresholds[status] + 12_345 + 17 + offset),
                "short_term_capital_gains": -(
                    2_000 + capital_caps[status] + offset + 700
                ),
                "long_term_capital_gains": 700,
                "non_sch_d_capital_gains": 2_000,
            }
            dependent = {
                **ZERO,
                "estate_income": -800_000,
                "partnership_income": 400_000,
                "short_term_capital_gains": -400_000,
                "long_term_capital_gains": 100_000,
                "non_sch_d_capital_gains": 200_000,
            }
            units.append(
                {
                    "status": status,
                    "other": 17,
                    "members": [(head, False), (dependent, True)],
                }
            )
    return units


def _pre_extraction_reference(unit, threshold, capital_cap):
    """Independent scalar reference, retaining the former one final cast."""
    business_income = max(0, unit["other"])
    business_losses = max(0, -unit["other"])
    capital_losses = gains_in_gross_income = 0
    for person, dependent in unit["members"]:
        if dependent:
            continue
        business_sources = (
            person["self_employment_income"] + person["sstb_self_employment_income"],
            person["farm_operations_income"],
            person["rental_income"],
            person["farm_rent_income"],
            person["estate_income"],
            person["partnership_income"] + person["s_corp_income"],
        )
        business_income += sum(max(0, value) for value in business_sources)
        business_losses += sum(max(0, -value) for value in business_sources)
        net_capital = (
            person["short_term_capital_gains"] + person["long_term_capital_gains"]
        )
        capital_losses += max(0, -net_capital)
        gains_in_gross_income += max(0, net_capital) + max(
            0, person["non_sch_d_capital_gains"]
        )
    business = min(business_losses, business_income + threshold)
    against_gains = min(capital_losses, gains_in_gross_income)
    net_capital_loss = min(capital_cap, capital_losses - against_gains)
    combined = business + against_gains + net_capital_loss
    # Check every total, not only individual leaf inputs: an intermediate
    # sum outside this domain can round before the final combined deduction.
    assert (
        max(
            business_income + threshold,
            business_losses,
            capital_losses,
            gains_in_gross_income,
            combined,
        )
        < EXACT_INTEGER_LIMIT
    )
    return np.float32(combined)


@pytest.mark.parametrize("year", [2021, 2025, 2026])
def test_whole_dollar_loss_ald_matches_pre_extraction_formula(system, year):
    """Dependent masking, status limits and source offsets preserve exact totals."""
    p = system.parameters(f"{year}-01-01").gov.irs.ald.loss
    thresholds = {status: p.max[status] for status in STATUSES}
    capital_caps = {status: p.capital.max[status] for status in STATUSES}
    units = _draw_units(year, thresholds, capital_caps)
    people, tax_units = {}, {}
    for i, unit in enumerate(units):
        members = []
        for j, (amounts, dependent) in enumerate(unit["members"]):
            name = f"u{i}_p{j}"
            members.append(name)
            people[name] = {
                "is_tax_unit_dependent": {year: dependent},
                **{name: {year: value} for name, value in amounts.items()},
            }
        tax_units[f"t{i}"] = {
            "members": members,
            "filing_status": {year: unit["status"]},
            "other_net_gain": {year: unit["other"]},
        }
    simulation = Simulation(
        tax_benefit_system=system,
        situation={"people": people, "tax_units": tax_units},
    )
    expected = np.array(
        [
            _pre_extraction_reference(
                unit, thresholds[unit["status"]], capital_caps[unit["status"]]
            )
            for unit in units
        ],
        dtype=np.float32,
    )
    actual = simulation.calculate("loss_ald", year)
    assert actual.dtype == np.float32
    np.testing.assert_array_equal(actual, expected)
