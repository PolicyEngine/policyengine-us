from policyengine_us.model_api import *


class medicaid_ltss_non_delaware_assistance_unit_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid LTSS assistance unit size outside Delaware"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit assistance-unit size for states outside Delaware. Use two "
        "only where the state budgets both spouses as a couple, including "
        "Texas spouses in the same institutional setting, and one for an "
        "individual applicant. Zero and unsupported sizes fail closed. "
        "Delaware ignores this input and derives the unit from the spouses' "
        "service, location, and duration facts. A separate input preserves "
        "Delaware derivation in mixed-state populations: providing values "
        "for some people on a derived variable fills the other people's "
        "entries with its default and overrides the formula for everyone."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/g-6100-institutional-eligibility-budgets",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-436",
    )
