from policyengine_us.model_api import *


class tx_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
        "https://www.law.cornell.edu/regulations/texas/title-1/part-15/chapter-372/subchapter-B",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Must have at least one eligible child in certified group
        # (eligible child already includes immigration and SSI checks)
        has_eligible_child = spm_unit.any(
            person("tx_tanf_eligible_child", period)
        )

        # Financial eligibility
        income_eligible = spm_unit("tx_tanf_income_eligible", period)
        resources_eligible = spm_unit("tx_tanf_resources_eligible", period)

        return has_eligible_child & income_eligible & resources_eligible
