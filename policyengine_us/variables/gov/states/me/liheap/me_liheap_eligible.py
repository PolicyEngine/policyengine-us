from policyengine_us.model_api import *


class me_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maine LIHEAP program"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = [
        "https://www.mainehousing.org/programs-services/energy/energydetails/liheap",
        "docs/agents/sources/me-liheap/income_eligibility_guidelines.md",
        "docs/agents/sources/me-liheap/federal_regulations.md",
        "42 U.S.C. § 8624 - Application and eligibility requirements",
    ]

    def formula(spm_unit, period, parameters):
        # Maine LIHEAP eligibility requirements based on documentation:
        # 1. Must meet income eligibility requirements
        # 2. Must be Maine resident (enforced by defined_for)

        income_eligible = spm_unit("me_liheap_income_eligible", period)

        # Additional eligibility factors could include:
        # - Residency (handled by defined_for = StateCode.ME)
        # - Application during program year (August 1 - May 29)
        # - Other program-specific requirements

        return income_eligible
