from policyengine_us.model_api import *


class EmployerPremiumContribution(Enum):
    NONE = "NONE"  # Employer paid none of premiums.
    SOME = "SOME"
    ALL = "ALL"
    NA = "N/A"


class employer_contribution_to_health_insurance_premiums_category(Variable):
    value_type = Enum
    entity = Person
    label = "Extent to which employer paid health insurance premiums"
    definition_period = YEAR
    possible_values = EmployerPremiumContribution
    default_value = EmployerPremiumContribution.NONE
    documentation = (
        "The share of health insurance premiums paid by the person's employer. "
        "For the self-employed health insurance deduction, enter a qualifying "
        "plan's payments or reimbursements from the person's own partnership "
        "or S corporation in health_insurance_premiums, without recording "
        "those payments as employer contributions of SOME or ALL. This S "
        "corporation treatment applies to shareholders who own more than 2%. "
        "Retain contributions from an unrelated employer. See "
        "self_employed_health_insurance_employer_plan_eligible for the "
        "remaining coverage-flag limitations."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/i7206--2025.pdf#page=1",
        # PDF pages 3-4
        "https://www.irs.gov/pub/irs-drop/n-08-01.pdf#page=3",
    )
