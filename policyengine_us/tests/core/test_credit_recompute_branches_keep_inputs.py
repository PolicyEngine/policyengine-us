"""Pinned-rules credit branches read the inputs their parent was given.

Four formulas recompute a federal credit under pinned rules in a branch:
``ny_eitc`` (pre-ARPA EITC, TY2021), ``al_federal_income_tax_deduction``
(2020 IRC, TY2021), and ``ny_ctc_pre_2024`` and ``ny_ctc_pre_2024_eligible``
(pre-TCJA CTC). Each drops the branch's values for the variables it
recalculates, chosen by name. Deleting them with ``Simulation.delete_arrays``
also deleted inputs with matching names, so the branch fell back to their
defaults: an EITC non-taker got the New York EITC, for example.

For each branch, the test supplies an input whose name matches the branch's
selection and checks the state output follows the input, not its default.
YAML can't separate the two readings for the CTC branches, because no plain
input has "ctc" in its name; there the input is a supplied value for a
formula variable, which the branch must keep too.
"""

import pytest

from policyengine_us import Simulation


def _parent_and_child(year, state, wages, child_age, tax_unit=None):
    tax_unit = dict(tax_unit or {})
    return {
        "people": {
            "parent": {
                "age": {year: 35},
                "employment_income": {year: wages},
            },
            "child": {"age": {year: child_age}},
        },
        "tax_units": {
            "tax_unit": {"members": ["parent", "child"], **tax_unit},
        },
        "spm_units": {"spm_unit": {"members": ["parent", "child"]}},
        "households": {
            "household": {
                "members": ["parent", "child"],
                "state_code": {year: state},
            }
        },
    }


def _calculate(situation, variable, year):
    return float(Simulation(situation=situation).calculate(variable, year)[0])


@pytest.mark.parametrize("takes_up", [True, False])
def test_ny_pre_arpa_eitc_branch_reads_takes_up_eitc(takes_up):
    situation = _parent_and_child(
        2021, "NY", 10_000, 3, {"takes_up_eitc": {2021: takes_up}}
    )
    # Pre-ARPA EITC: 34% x $10,000 = $3,400; NY matches 30% = $1,020.
    expected = 1_020 if takes_up else 0
    assert _calculate(situation, "ny_eitc", 2021) == pytest.approx(expected)


@pytest.mark.parametrize("takes_up, expected", [(True, 258.87), (False, 380)])
def test_al_2020_irc_branch_reads_takes_up_eitc(takes_up, expected):
    # Part II: $2,380 federal tax - $2,000 nonrefundable 2020-rule CTC = $380,
    # less the 2020-rule EITC of $121.13 only when the filer takes it up.
    situation = _parent_and_child(
        2021, "AL", 41_000, 3, {"takes_up_eitc": {2021: takes_up}}
    )
    assert _calculate(
        situation, "al_federal_income_tax_deduction", 2021
    ) == pytest.approx(expected, abs=0.01)


def test_ny_pre_tcja_ctc_eligibility_branch_reads_supplied_qualifying_child():
    situation = _parent_and_child(2023, "NY", 30_000, 6)
    assert _calculate(situation, "ny_ctc_pre_2024_eligible", 2023) == 1
    situation["people"]["child"]["ctc_qualifying_child"] = {2023: False}
    assert _calculate(situation, "ny_ctc_pre_2024_eligible", 2023) == 0


def test_ny_pre_tcja_ctc_branch_reads_supplied_ctc():
    situation = _parent_and_child(2023, "NY", 30_000, 6)
    # Pre-TCJA CTC $1,000 for one child; NY pays 33% = $330.
    assert _calculate(situation, "ny_ctc_pre_2024", 2023) == pytest.approx(330)
    # A supplied federal CTC of zero carries into the pinned recomputation,
    # leaving the $100-per-child minimum.
    situation["tax_units"]["tax_unit"]["ctc"] = {2023: 0}
    assert _calculate(situation, "ny_ctc_pre_2024", 2023) == pytest.approx(100)
