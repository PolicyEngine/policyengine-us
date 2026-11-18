from policyengine_us.model_api import *


class medicaid_ltss_non_delaware_assistance_unit_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid LTSS assistance unit size outside Delaware"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Candidate assistance-unit size for states outside Delaware. Report "
        "two for Texas spouses in the same institutional setting who must "
        "be tested as a couple first. Under G-6120, the derived unit falls "
        "back to one for each spouse if the couple exceeds either its "
        "income or resource limit. Report one for spouses in separate "
        "institutional settings and individual applicants. A community "
        "spouse is inconsistent with a couple unit and prevents that "
        "fallback, preserving the resource screen's fail-closed result. "
        "Zero and unsupported sizes fail closed. "
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
