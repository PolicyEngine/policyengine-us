"""Per-contract inputs for annuity contracts held outside qualified plans
(IRC 72(b), (c), (e)). Three slots per person, one contract each. Contracts
issued by the same company to the same owner in one calendar year are
aggregated under IRC 72(e)(12): put them in one slot. A 1035 exchange is not
a taxable event; carry the old contract's investment into the new slot. For
partial annuitization (IRC 72(a)(2)), set annuitized_share so the investment
is split between annuity payments and withdrawals.

Amounts here must not also be reported in taxable_pension_income."""

from policyengine_us.model_api import *

ANNUITY_CONTRACT_SLOTS = 3
_REF = (
    "https://www.law.cornell.edu/uscode/text/26/72",
    "https://www.irs.gov/publications/p939",
)
_FIELDS = {
    "annuity_payments": (
        float,
        USD,
        "Payments received as an annuity",
        "Amounts received as an annuity under the contract this year (IRC 72(a)).",
    ),
    "investment_in_contract": (
        float,
        USD,
        "Investment in the contract",
        "Premiums paid less amounts previously received tax-free, adjusted for any refund feature (IRC 72(c)(1), (2)).",
    ),
    "expected_return": (
        float,
        USD,
        "Expected return at the annuity starting date",
        "Total expected return (IRC 72(c)(3)) from the Treas. Reg. 1.72-9 tables; sets the exclusion ratio.",
    ),
    "investment_recovered": (
        float,
        USD,
        "Investment already recovered tax-free",
        "Cumulative amounts excluded in prior years under the exclusion ratio.",
    ),
    "starting_date_before_1987": (
        bool,
        None,
        "Annuity starting date before 1987",
        "For starting dates before 1987 the exclusion continues after the investment is recovered (IRC 72(b)(2) applies only after 1986).",
    ),
    "annuitized_share": (
        float,
        "/1",
        "Share of the contract annuitized",
        "Partial annuitization: share of the investment allocated to the annuity payments; 0 is read as 1 when there are annuity payments.",
    ),
    "withdrawals": (
        float,
        USD,
        "Amounts not received as an annuity",
        "Withdrawals, partial surrenders and other amounts not received as an annuity (IRC 72(e)).",
    ),
    "cash_value": (
        float,
        USD,
        "Cash value immediately before the withdrawals",
        "Cash value of the contract before the withdrawals (IRC 72(e)(3)).",
    ),
    "pre_august_1982_investment": (
        float,
        USD,
        "Investment made before August 14, 1982",
        "Remaining investment from before August 14, 1982; withdrawals recover it first, tax-free (IRC 72(e)(5)(B)).",
    ),
}

for _slot in range(1, ANNUITY_CONTRACT_SLOTS + 1):
    for _field, (_type, _unit, _label, _doc) in _FIELDS.items():
        _name = f"annuity_contract_{_slot}_{_field}"
        _attrs = dict(
            value_type=_type,
            entity=Person,
            definition_period=YEAR,
            label=f"Annuity contract {_slot}: {_label.lower()}",
            documentation=_doc,
            reference=_REF,
            __module__=__name__,
        )
        if _unit:
            _attrs["unit"] = _unit
        globals()[_name] = type(_name, (Variable,), _attrs)
