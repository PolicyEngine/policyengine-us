"""Simplified Method inputs (IRC 72(d)) for annuities from qualified plans,
403(b) plans and IRAs-in-annuity-form with after-tax cost. The gross payments
here must not also be reported in taxable_pension_income."""

from policyengine_us.model_api import *

_REF = (
    "https://www.law.cornell.edu/uscode/text/26/72#d",
    "https://www.irs.gov/publications/p575",
)


def _input(name, value_type, label, documentation, unit=None):
    attributes = dict(
        value_type=value_type,
        entity=Person,
        definition_period=YEAR,
        label=label,
        documentation=documentation,
        reference=_REF,
        __module__=__name__,
    )
    if unit:
        attributes["unit"] = unit
    globals()[name] = type(name, (Variable,), attributes)


_input(
    "qualified_annuity_gross_payments",
    float,
    "Gross qualified plan annuity payments with after-tax cost",
    "Gross annuity payments this year from a qualified plan annuity with an annuity starting date after November 18, 1996 (Form 1099-R box 1).",
    USD,
)
_input(
    "qualified_annuity_cost",
    float,
    "Cost in the qualified plan annuity",
    "After-tax contributions (investment in the contract) at the annuity starting date.",
    USD,
)
_input(
    "qualified_annuity_monthly_payments_this_year",
    int,
    "Monthly payments received this year",
    "Number of monthly payments received this year.",
)
_input(
    "qualified_annuity_starting_age",
    int,
    "Annuitant's age at the annuity starting date",
    "Age at the annuity starting date (single life).",
)
_input(
    "qualified_annuity_combined_starting_age",
    int,
    "Combined ages at the starting date for a joint annuity",
    "Sum of the annuitants' ages for a joint and survivor annuity; 0 for a single-life annuity.",
)
_input(
    "qualified_annuity_cost_recovered",
    float,
    "Cost already recovered tax-free",
    "Amounts excluded in earlier years under the Simplified Method.",
    USD,
)
