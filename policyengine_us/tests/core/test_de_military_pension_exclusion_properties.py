"""Properties of Delaware's pension exclusion for military pensions, 2022-2031.

30 Del. C. 1106(b)(3) subtracts, for 2022 through 2026, the greater of
pensions up to $2,000 and a United States military pension up to $12,500 for
a person under 60, and pensions and eligible retirement income up to $12,500
for a person 60 or older. For 2027, 2028 and from 2029 ((b)(3)c, d and e) the
military cap is $15,000, $20,000 and $25,000, and a person 60 or older takes
the greater of the $12,500 exclusion and the military pension up to that cap.
From 2027 ((b)(3)f.4), a person 60 or older who fails the domicile requirement
gets no subtraction.

A United States military pension is "a pension received as a result of an
individual's service" ((b)(3)f.2, added by 84 Del. Laws c. 437 in 2024), so
from 2024 it is a retiree's own pay plus an annuity paid to a member's
survivor. For 2022 and 2023, when the term had no definition, it is the
retiree's own pay.

The reference below restates those rules from the statute, not from the
model's parameters. Hypothesis draws batches of single filers (any age;
military retired pay, survivor annuities, other pensions, IRA distributions,
interest, capital gains or losses, and the domicile requirement), runs each
batch as one simulation with the same inputs in every year, and checks for
every filer and year:

1. The exclusion equals the reference amount.
2. It is never negative and never exceeds the retired pay and survivor
   annuity plus the pension basket floored at zero.
3. From 2027, a filer 60 or older who meets the domicile requirement never
   gets less than the 2026 rule gives.
4. From 2024, exchanging a filer's retired pay and survivor annuity leaves
   the exclusion unchanged. Each batch carries every filer's twin with the
   two amounts exchanged, so this check does not rest on the reference.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = tuple(range(2022, 2032))
MILITARY_CAP = {2027: 15_000, 2028: 20_000}


def military_cap(year):
    if year <= 2026:
        return 12_500
    return MILITARY_CAP.get(year, 25_000)


def basket(filer):
    """Pensions and eligible retirement income, with the $3,000 loss limit."""
    gains = max(filer["long_term_capital_gains"], -3_000)
    return (
        filer["military_retirement_pay"]
        + filer["military_retirement_pay_survivors"]
        + filer["taxable_pension_income"]
        + filer["taxable_ira_distributions"]
        + filer["taxable_interest_income"]
        + gains
    )


def military_pension(year, filer):
    """Retired pay, plus a survivor's annuity from 2024."""
    if year <= 2023:
        return filer["military_retirement_pay"]
    return filer["military_retirement_pay"] + filer["military_retirement_pay_survivors"]


def reference(year, filer):
    military = min(military_cap(year), military_pension(year, filer))
    if (
        year >= 2027
        and filer["age"] >= 60
        and not filer["de_pension_exclusion_domicile_requirement_met"]
    ):
        return 0
    if filer["age"] < 60:
        pensions = (
            filer["taxable_pension_income"]
            + filer["military_retirement_pay"]
            + filer["military_retirement_pay_survivors"]
        )
        return max(min(2_000, max(pensions, 0)), military)
    general = min(12_500, max(basket(filer), 0))
    if year <= 2026:
        return general
    return max(general, military)


filers = st.fixed_dictionaries(
    {
        "age": st.integers(30, 90),
        "military_retirement_pay": st.sampled_from(
            [0, 1_000, 12_500, 15_000, 18_000, 20_000, 25_000, 40_000]
        ),
        "military_retirement_pay_survivors": st.sampled_from([0, 3_000, 30_000]),
        "taxable_pension_income": st.sampled_from([0, 1_500, 20_000]),
        "taxable_ira_distributions": st.sampled_from([0, 5_000, 20_000]),
        "taxable_interest_income": st.sampled_from([0, 2_000]),
        "long_term_capital_gains": st.sampled_from([-10_000, -2_000, 0, 4_000]),
        "de_pension_exclusion_domicile_requirement_met": st.booleans(),
    }
)


def exchanged(filer):
    """The same filer with retired pay and the survivor annuity exchanged."""
    return {
        **filer,
        "military_retirement_pay": filer["military_retirement_pay_survivors"],
        "military_retirement_pay_survivors": filer["military_retirement_pay"],
    }


def simulate(batch):
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    for i, filer in enumerate(batch):
        name = f"filer_{i}"
        people[name] = {k: {y: v for y in YEARS} for k, v in filer.items()}
        tax_units[f"tax_unit_{i}"] = {
            "members": [name],
            "filing_status": {y: "SINGLE" for y in YEARS},
        }
        households[f"household_{i}"] = {
            "members": [name],
            "state_code": {y: "DE" for y in YEARS},
        }
        for group in groups:
            groups[group][f"{group}_{i}"] = {"members": [name]}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        }
    )


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(batch=st.lists(filers, min_size=10, max_size=30))
def test_military_pension_exclusion(batch):
    simulation = simulate(batch + [exchanged(filer) for filer in batch])
    for year in YEARS:
        exclusion = np.asarray(simulation.calculate("de_pension_exclusion", year))
        amounts, twin_amounts = exclusion[: len(batch)], exclusion[len(batch) :]
        for filer, amount, twin_amount in zip(batch, amounts, twin_amounts):
            assert amount == reference(year, filer), (year, filer, amount)
            received = (
                filer["military_retirement_pay"]
                + filer["military_retirement_pay_survivors"]
            )
            assert 0 <= amount <= received + max(basket(filer), 0)
            if (
                year >= 2027
                and filer["age"] >= 60
                and filer["de_pension_exclusion_domicile_requirement_met"]
            ):
                assert amount >= reference(2026, filer)
            if year >= 2024:
                assert amount == twin_amount, (year, filer, amount, twin_amount)
