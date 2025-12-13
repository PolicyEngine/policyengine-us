from policyengine_us.model_api import *


class me_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine LIHEAP countable income"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = [
        "https://www.mainehousing.org/programs-services/energy/energydetails/liheap",
        "docs/agents/sources/me-liheap/income_eligibility_guidelines.md",
        "42 U.S.C. § 8624(b)(2) - Income eligibility requirements",
    ]

    def formula(spm_unit, period, parameters):
        # Maine LIHEAP uses gross household income for eligibility determination
        # Based on documentation: "Gross household income based on household size"
        return add(spm_unit, period, ["irs_gross_income"])
