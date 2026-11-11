"""Calculator-off reported amounts preserve the complete reform comparison."""

from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us.tests.unit.test_ss_calculator_differential import (
    YEAR,
    _assert_reported_matches_reference,
    _pia_reform,
    _reported_retirement_and_disability,
)


@settings(max_examples=3, deadline=None, derandomize=True, database=None)
@example(retirement_cents=0, disability_cents=0)
@example(retirement_cents=84, disability_cents=120)
@example(retirement_cents=1_811_712, disability_cents=2_588_160)
@given(
    retirement_cents=st.one_of(
        st.just(0), st.integers(min_value=84, max_value=6_000_000)
    ),
    disability_cents=st.one_of(
        st.just(0), st.integers(min_value=120, max_value=6_000_000)
    ),
)
def test_reported_amounts_preserve_calculator_off_reform_outputs(
    retirement_cents, disability_cents
):
    # Draw zero or whole cents with a positive dime-rounded baseline PIA.
    # Compare SSA outputs, downstream outputs and cached reference intermediates
    # under the same PIA reform.
    situation = _reported_retirement_and_disability()
    situation["people"]["retiree"]["social_security_retirement_reported"][YEAR] = (
        retirement_cents / 100
    )
    situation["people"]["disabled"]["social_security_disability_reported"][YEAR] = (
        disability_cents / 100
    )
    _assert_reported_matches_reference(situation, _pia_reform())
