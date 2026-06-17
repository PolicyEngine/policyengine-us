from policyengine_us.model_api import *


class chip_gross(Variable):
    value_type = float
    entity = Person
    label = "Gross CHIP benefit value"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.macpac.gov/publication/chip-spending-by-state/",
        "https://www.medicaid.gov/medicaid/financial-management/state-expenditure-reporting-for-medicaid-chip/expenditure-reports-mbescbes",
    )
    documentation = (
        "Gross CHIP service value for a CHIP-eligible person, equal to the "
        "per-capita net CHIP spending plus the state's household cost-sharing "
        "offsets. This is eligibility-gated rather than enrollment-gated, "
        "and is the counterpart to `chip`, which is the enrolled "
        "net-of-premium value reported by MACPAC. Use this only when a gross "
        "eligible-value concept is needed and enrollment take-up is modeled "
        "separately."
    )
    defined_for = "is_chip_eligible"
    adds = ["per_capita_chip_gross"]
