"""Form 8853 Section C inputs, entered on the insured (chronically or
terminally ill) person, aggregating every contract that covers them."""

from policyengine_us.model_api import *

_REF = (
    "https://www.law.cornell.edu/uscode/text/26/7702B#d",
    "https://www.irs.gov/instructions/i8853",
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
    "long_term_care_per_diem_benefits",
    float,
    "Per diem long-term care benefits received",
    "Gross per diem or other periodic payments under qualified long-term care insurance contracts and per diem accelerated death benefits (Form 1099-LTC box 1 or 2, per diem basis).",
    USD,
)
_input(
    "long_term_care_per_diem_days",
    int,
    "Days in the long-term care period",
    "Days in the period(s) for which the per diem payments were made (Form 8853 line 18).",
)
_input(
    "long_term_care_qualified_costs",
    float,
    "Qualified long-term care services costs incurred",
    "Costs incurred for qualified long-term care services in the period (Form 8853 line 19).",
    USD,
)
_input(
    "long_term_care_cost_reimbursements",
    float,
    "Reimbursements of long-term care costs",
    "Reimbursements for those services received from other sources (Form 8853 line 21).",
    USD,
)
