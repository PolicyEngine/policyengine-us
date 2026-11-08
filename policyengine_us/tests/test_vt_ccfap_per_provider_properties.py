"""Vermont's child care family balance, provider by provider.

Vermont's family booklet (CCFAP-Family-Booklet, PDF page 10) has the family pay
its weekly share to the youngest child's provider first, with what's left going
to the next provider. The state pays each provider the child's rate less the
share assigned there, and each program's invoice takes that payment off that
child's tuition (CDD-Memo-UPK-and-CCFAP-family-tuition, PDF pages 1 and 6). A
payment above one child's tuition stays with that program (the same memo, PDF
page 4), so it pays none of another child's bill.

For families of up to three children with any ages, care hours, provider types,
bills and share:

1. Each child's assigned share, state payment and payment above its bill match
   a separate month-by-month reimplementation of the booklet's order and the
   memo's invoices, which reads only the model's state rates.
2. With a bill, the family owes each child's program between nothing and that
   child's whole bill.
3. With a bill, the family's child care expense equals the sum of what it owes
   each program. With none, it owes nothing and household benefits count the
   whole subsidy.
4. With a bill, the subsidy counted in household benefits and the family's
   expense add up to the bill, so household benefits never exceed it.
5. Each month the state pays the children's rates less the share, floored at
   zero, the same total as one payment against the whole bill.
6. An older child's provider takes share only once each younger child's rate
   is full. Children of the same age take it in the order the unit lists them.
7. A family with one child gets the one-payment result: the family owes the
   bill less the subsidy, floored at zero, and household benefits count the
   subsidy up to the bill.
8. Through 2023 the state paid no more than each provider charged, so no
   payment exceeds its child's bill and netting the whole bill gives the same
   expense.
9. With Vermont's subsidy set to zero, the family owes its whole bill and
   household benefits count nothing.

The YAML cases pin the booklet's and the memo's families. These generate
families that YAML can't enumerate.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

WEEKS = 52
MONTHS = 12
# Annual dollars, about two cents a week.
TOLERANCE = 1.0
MONTHLY_TOLERANCE = 0.01
PROVIDERS = ["LICENSED_CENTER", "REGISTERED_HOME"]
# gov.states.vt.dcf.ccfap.age_threshold.base
AGE_LIMIT = 13


def child_strategy(min_age=0, max_age=17, min_bill=0):
    return st.fixed_dictionaries(
        {
            "age": st.integers(min_value=min_age, max_value=max_age),
            "hours": st.integers(min_value=0, max_value=60),
            "provider": st.integers(min_value=0, max_value=1),
            "bill": st.integers(min_value=min_bill, max_value=800),
        }
    )


def family_strategy(min_size=1, max_size=3, **child_kwargs):
    return st.lists(
        child_strategy(**child_kwargs), min_size=min_size, max_size=max_size
    ).map(lambda kids: {f"child{i}": kid for i, kid in enumerate(kids)})


def situation(children, weekly_share, year, subsidy=None):
    members = ["parent", *children]
    people = {"parent": {"age": {year: 30}}}
    for name, child in children.items():
        person = {
            "age": {year: child["age"]},
            "is_tax_unit_dependent": {year: True},
            "vt_ccfap_provider_type": {year: PROVIDERS[child["provider"]]},
            "pre_subsidy_childcare_expenses": {year: child["bill"] * WEEKS},
        }
        if child["hours"]:
            person["childcare_hours_per_week"] = {year: child["hours"]}
        people[name] = person
    spm_unit = {
        "members": members,
        "vt_ccfap_eligible": {year: True},
        "vt_ccfap_family_share": {year: weekly_share * WEEKS},
    }
    if subsidy is not None:
        spm_unit["vt_child_care_subsidies"] = {year: subsidy}
    return {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": spm_unit},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {year: "VT"}}},
    }


def months(year):
    return [f"{year}-{month:02d}" for month in range(1, MONTHS + 1)]


def model(children, weekly_share, year, subsidy=None):
    """The model's yearly amounts, and its monthly rates and assigned shares.

    Person arrays leave out the parent, so they follow the children's order.
    """
    simulation = Simulation(situation=situation(children, weekly_share, year, subsidy))

    def children_of(name, period=year):
        return np.array(simulation.calculate(name, period)[1:], dtype=float)

    def unit(name):
        return float(simulation.calculate(name, year)[0])

    def pays_above(month):
        parameters = simulation.tax_benefit_system.parameters(f"{month}-01")
        return bool(parameters.gov.states.vt.dcf.ccfap.rates.pays_above_provider_charge)

    return dict(
        bill=children_of("vt_ccfap_child_bill"),
        assigned=children_of("vt_ccfap_assigned_family_share"),
        payment=children_of("vt_ccfap_child_payment"),
        above=children_of("vt_ccfap_payment_above_bill"),
        subsidies=unit("child_care_subsidies"),
        above_bills=unit("child_care_subsidies_above_provider_bills"),
        expense=unit("childcare_expenses"),
        counted=unit("household_child_care_subsidies"),
        weekly_state_rates=[
            children_of("vt_ccfap_state_rate", m) for m in months(year)
        ],
        monthly_rates=[children_of("vt_ccfap_child_rate", m) for m in months(year)],
        monthly_assigned=[
            children_of("vt_ccfap_assigned_family_share", m) for m in months(year)
        ],
        pays_above=[pays_above(m) for m in months(year)],
    )


def reference(children, weekly_share, weekly_state_rates, pays_above):
    """Each program's invoice, month by month, from the booklet's order.

    Once a child has care hours, the children with hours carry the bills of the
    children without them (the attendance rule); with no hours anywhere, each
    child with a bill is in care.
    """
    kids = list(children.values())
    bills = np.array([kid["bill"] * WEEKS for kid in kids], dtype=float)
    hours = np.array([kid["hours"] for kid in kids])
    ages = np.array([kid["age"] for kid in kids])
    eligible = ages < AGE_LIMIT
    if (hours > 0).any():
        in_care = hours > 0
        moved = bills[~in_care].sum() / in_care.sum()
        annual_bill = np.where(in_care, bills + moved, 0)
    else:
        in_care = bills > 0
        annual_bill = np.where(in_care, bills, 0)
    payment = np.zeros(len(kids))
    assigned_total = np.zeros(len(kids))
    for state_rate, state_pays_above in zip(weekly_state_rates, pays_above):
        weekly_rate = state_rate
        if not state_pays_above:
            capped = np.minimum(state_rate, annual_bill / WEEKS)
            weekly_rate = np.where(annual_bill > 0, capped, state_rate)
        rate = np.where(in_care & eligible, weekly_rate * WEEKS / MONTHS, 0)
        remaining = weekly_share * WEEKS / MONTHS
        assigned = np.zeros(len(kids))
        youngest_first = sorted(
            (i for i in range(len(kids)) if rate[i] > 0), key=lambda i: (ages[i], i)
        )
        for i in youngest_first:
            assigned[i] = min(remaining, rate[i])
            remaining -= assigned[i]
        payment += rate - assigned
        assigned_total += assigned
    if bills.sum() > 0:
        above = np.maximum(payment - annual_bill, 0)
    else:
        above = np.zeros(len(kids))
    return dict(
        bill=annual_bill,
        assigned=assigned_total,
        payment=payment,
        above=above,
        owed=np.maximum(annual_bill - payment, 0),
    )


def kid(age, hours, provider, bill):
    return dict(age=age, hours=hours, provider=provider, bill=bill)


@settings(max_examples=25, deadline=None)
# An infant at a 360 center and a preschooler at a 325 center with a 200 share:
# the family owes 65 at the infant's center.
@example(
    children={"infant": kid(0, 35, 0, 360), "preschooler": kid(3, 35, 0, 325)},
    weekly_share=200,
    year=2026,
)
# The memo's invoice (350 tuition, 300 share) beside a school-age sibling whose
# 204 part-time rate exceeds a 150 tuition.
@example(
    children={"preschooler": kid(3, 35, 0, 350), "schoolchild": kid(7, 15, 0, 150)},
    weekly_share=300,
    year=2026,
)
# The share fills the infant's 223 rate and spills 77 onto the next provider.
@example(
    children={"infant": kid(0, 15, 1, 200), "preschooler": kid(3, 35, 0, 300)},
    weekly_share=300,
    year=2026,
)
# No hours anywhere: a teenager carries a share of the bill with no payment.
@example(
    children={"preschooler": kid(3, 0, 0, 150), "teenager": kid(15, 0, 0, 150)},
    weekly_share=50,
    year=2026,
)
# Same-age children, a share above every rate, a child without hours whose bill
# moves to the children in care, and no bill at all.
@example(
    children={"first": kid(2, 30, 0, 100), "second": kid(2, 30, 1, 500)},
    weekly_share=300,
    year=2024,
)
@example(
    children={
        "toddler": kid(2, 20, 1, 220),
        "preschooler": kid(4, 20, 1, 200),
        "schoolchild": kid(9, 10, 1, 90),
    },
    weekly_share=600,
    year=2026,
)
@example(
    children={"infant": kid(0, 40, 0, 300), "sibling": kid(8, 0, 1, 400)},
    weekly_share=100,
    year=2024,
)
@example(
    children={"infant": kid(0, 40, 0, 0), "preschooler": kid(3, 40, 1, 0)},
    weekly_share=75,
    year=2026,
)
@given(
    children=family_strategy(),
    weekly_share=st.integers(min_value=0, max_value=600),
    year=st.sampled_from([2024, 2026]),
)
def test_each_program_nets_its_own_payment(children, weekly_share, year):
    got = model(children, weekly_share, year)
    want = reference(
        children, weekly_share, got["weekly_state_rates"], got["pays_above"]
    )
    # 1. The model matches the separate reimplementation.
    for key in ("bill", "assigned", "payment", "above"):
        assert got[key] == pytest.approx(want[key], abs=TOLERANCE), key
    bill = sum(child["bill"] for child in children.values()) * WEEKS
    assert got["counted"] >= -TOLERANCE
    if bill > 0:
        # 2. What the family owes each program lies between nothing and its
        # bill.
        owed = got["bill"] - (got["payment"] - got["above"])
        assert (owed >= -TOLERANCE).all()
        assert (owed <= got["bill"] + TOLERANCE).all()
        assert owed == pytest.approx(want["owed"], abs=TOLERANCE)
        # 3. The family's expense sums what it owes each program.
        assert got["expense"] == pytest.approx(owed.sum(), abs=TOLERANCE)
        # 4. Counted subsidy and expense add up to the bill.
        assert got["counted"] <= bill + TOLERANCE
        assert got["counted"] + got["expense"] == pytest.approx(bill, abs=TOLERANCE)
    else:
        # With no bill recorded, the providers' charges are unknown: the family
        # owes nothing and household benefits count the whole subsidy.
        assert got["expense"] == pytest.approx(0, abs=TOLERANCE)
        assert got["counted"] == pytest.approx(got["subsidies"], abs=TOLERANCE)
    # 5. The state's monthly total is the rates less the share, floored at zero.
    monthly_share = weekly_share * WEEKS / MONTHS
    total = sum(max(rates.sum() - monthly_share, 0) for rates in got["monthly_rates"])
    assert got["subsidies"] == pytest.approx(total, abs=TOLERANCE)
    assert got["above_bills"] == pytest.approx(got["above"].sum(), abs=TOLERANCE)
    # 6. Youngest first: an older child takes share only once each younger
    # child's rate is full.
    ages = [child["age"] for child in children.values()]
    for rates, assigned in zip(got["monthly_rates"], got["monthly_assigned"]):
        for older in range(len(ages)):
            if assigned[older] <= MONTHLY_TOLERANCE:
                continue
            for younger in range(len(ages)):
                ahead = (ages[younger], younger) < (ages[older], older)
                if ahead and rates[younger] > 0:
                    assert assigned[younger] == pytest.approx(
                        rates[younger], abs=MONTHLY_TOLERANCE
                    )


@settings(max_examples=15, deadline=None)
# A bill below the state's payment, a bill above the state rate, no bill, and a
# share above the rate.
@example(child=kid(3, 35, 0, 100), weekly_share=300, year=2026)
@example(child=kid(1, 35, 1, 600), weekly_share=50, year=2024)
@example(child=kid(5, 10, 0, 0), weekly_share=0, year=2026)
@example(child=kid(0, 60, 0, 700), weekly_share=700, year=2023)
@given(
    child=child_strategy(max_age=12),
    weekly_share=st.integers(min_value=0, max_value=700),
    year=st.sampled_from([2023, 2024, 2026]),
)
def test_one_child_gets_the_one_payment_result(child, weekly_share, year):
    got = model({"child": child}, weekly_share, year)
    bill = child["bill"] * WEEKS
    subsidies = got["subsidies"]
    assert got["expense"] == pytest.approx(max(bill - subsidies, 0), abs=TOLERANCE)
    counted = min(subsidies, bill) if bill > 0 else subsidies
    assert got["counted"] == pytest.approx(counted, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(
    children={"infant": kid(0, 35, 0, 360), "preschooler": kid(3, 35, 0, 325)},
    weekly_share=200,
)
@example(
    children={"infant": kid(1, 8, 1, 75), "preschooler": kid(3, 35, 0, 250)},
    weekly_share=100,
)
@given(
    # Every child carries a bill, so the state's rate never goes uncapped.
    children=family_strategy(min_size=2, min_bill=1),
    weekly_share=st.integers(min_value=0, max_value=600),
)
def test_through_2023_no_payment_exceeds_its_bill(children, weekly_share):
    got = model(children, weekly_share, 2023)
    assert (got["above"] <= TOLERANCE).all()
    assert got["above_bills"] == pytest.approx(0, abs=TOLERANCE)
    bill = sum(child["bill"] for child in children.values()) * WEEKS
    whole_bill_expense = max(bill - got["subsidies"], 0)
    assert got["expense"] == pytest.approx(whole_bill_expense, abs=TOLERANCE)


@settings(max_examples=10, deadline=None)
@example(
    children={"infant": kid(0, 35, 0, 360), "preschooler": kid(3, 35, 0, 325)},
    weekly_share=200,
    year=2026,
)
@given(
    children=family_strategy(min_size=2, max_age=12),
    weekly_share=st.integers(min_value=0, max_value=600),
    year=st.sampled_from([2024, 2026]),
)
def test_without_the_subsidy_the_family_owes_its_whole_bill(
    children, weekly_share, year
):
    got = model(children, weekly_share, year, subsidy=0)
    bill = sum(child["bill"] for child in children.values()) * WEEKS
    assert got["above_bills"] == pytest.approx(0, abs=TOLERANCE)
    assert got["expense"] == pytest.approx(bill, abs=TOLERANCE)
    assert got["counted"] == pytest.approx(0, abs=TOLERANCE)
