"""Regression tests for the Oregon Kids' Credit sunset (issue #9074).

HB 3235 (2023) Section 11 limits the credit to tax years beginning on or
after January 1, 2023, and before January 1, 2029. The sunset is encoded
solely in ``gov.states.or.tax.income.credits.ctc.in_effect`` (the credit
stays in the refundable-credits list), so a single parameter switch models
renewal scenarios.
"""

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import system


OR_CTC_PARAMS = system.parameters.gov.states.children["or"].tax.income.credits.ctc

SITUATION = {
    "people": {
        "parent": {"age": {"2028": 30, "2029": 31}},
        "child1": {"age": {"2028": 2, "2029": 3}},
        "child2": {"age": {"2028": 4, "2029": 5}},
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent", "child1", "child2"],
            "or_agi": {"2028": 10_000, "2029": 10_000},
        }
    },
    "households": {
        "household": {
            "members": ["parent", "child1", "child2"],
            "state_code": {"2028": "OR", "2029": "OR"},
        }
    },
}


def _renew_in_effect_from_2029():
    """A reform flipping only the in_effect switch back on from 2029."""

    class RenewFrom2029(Reform):
        def apply(self):
            def modify(parameters):
                node = parameters
                path = "gov.states.or.tax.income.credits.ctc.in_effect"
                for part in path.split("."):
                    node = getattr(node, part)
                node.update(
                    start=instant("2029-01-01"),
                    stop=instant("2100-12-31"),
                    value=True,
                )
                return parameters

            self.modify_parameters(modify)

    return RenewFrom2029


def test_or_ctc_pays_through_2028_and_stops_in_2029():
    sim = Simulation(situation=SITUATION)
    assert sim.calculate("or_ctc", 2028)[0] > 0
    assert sim.calculate("or_ctc", 2029)[0] == 0
    # The credit also drops out of the refundable-credit total (the family
    # qualifies for no other Oregon refundable credit).
    assert sim.calculate("or_refundable_credits", 2028)[0] > 0
    assert sim.calculate("or_refundable_credits", 2029)[0] == 0


def test_in_effect_reform_restores_the_credit_from_2029():
    sim = Simulation(situation=SITUATION, reform=_renew_in_effect_from_2029())
    p = sim.tax_benefit_system.parameters("2029-01-01")
    amount = p.gov.states["or"].tax.income.credits.ctc.amount
    expected = 2 * amount
    result = sim.calculate("or_ctc", 2029)[0]
    assert result == expected
    assert result > 0
    # The renewed credit flows through the refundable-credits list.
    assert sim.calculate("or_refundable_credits", 2029)[0] == expected


def test_amount_and_phase_out_start_uprate_beyond_last_known_values():
    """ORS 315.273(5) indexes both dollar amounts, flooring to $50 multiples."""
    amount_2028 = OR_CTC_PARAMS.amount("2028-01-01")
    start_2028 = OR_CTC_PARAMS.reduction.start("2028-01-01")
    assert amount_2028 > 1_050
    assert amount_2028 % 50 == 0
    assert start_2028 > 26_550
    assert start_2028 % 50 == 0
