"""Mid-year regression tests for the SNAP BBCE gross income limit.

States re-base their broad-based categorical eligibility standards to a
new year's federal poverty guidelines on their own schedule. Washington
re-bases each April 1 under WAC 388-414-0001(2)(a)(ii), while most states
follow the federal October fiscal-year cycle.

The YAML runner accepts only whole-year and first-month periods, so the
April boundary cannot be expressed there. These build the simulation
directly to check the months in between.

Run with:
    uv run pytest policyengine_us/tests/test_bbce_gross_income_limit_rebasing.py
"""

VARIABLE = "tanf_non_cash_gross_income_limit"

# 200% of the one-person guideline, monthly: 2025 guidelines give
# 15,650 / 12 x 2 = 2,608.33 and 2026 guidelines give 15,960 / 12 x 2 =
# 2,660. Washington publishes whole-dollar standards.
WA_LIMIT_ON_2025_GUIDELINES = 2_608
WA_LIMIT_ON_2026_GUIDELINES = 2_660
# Colorado takes the federal October cycle and publishes no rounding
# convention of its own.
CO_LIMIT_ON_2025_GUIDELINES = 2_608.33


def one_person_limit(state_code, period, year=2026):
    from policyengine_us import Simulation

    situation = {
        "people": {"person1": {"age": {year: 30}}},
        "spm_units": {"spm_unit": {"members": ["person1"]}},
        "households": {
            "household": {
                "members": ["person1"],
                "state_code": {year: state_code},
            }
        },
    }
    simulation = Simulation(situation=situation)
    return simulation.calculate(VARIABLE, period)[0]


def test_wa_limit_rebases_in_april():
    # March still uses the 2025 guidelines; April moves to the 2026 ones.
    assert one_person_limit("WA", "2026-03") == WA_LIMIT_ON_2025_GUIDELINES
    assert one_person_limit("WA", "2026-04") == WA_LIMIT_ON_2026_GUIDELINES


def test_wa_limit_holds_the_new_guidelines_through_september():
    # The federal October re-basing must not disturb Washington's own
    # standard, which already moved in April.
    for month in ["04", "05", "09", "10", "12"]:
        assert one_person_limit("WA", f"2026-{month}") == WA_LIMIT_ON_2026_GUIDELINES


def test_wa_leads_october_cycle_states_between_april_and_september():
    # Guard against a vacuous pass: an October-cycle state stays on the
    # 2025 guidelines in the months where Washington has already moved.
    assert one_person_limit("CO", "2026-04") == CO_LIMIT_ON_2025_GUIDELINES
    assert one_person_limit("WA", "2026-04") > one_person_limit("CO", "2026-04")
