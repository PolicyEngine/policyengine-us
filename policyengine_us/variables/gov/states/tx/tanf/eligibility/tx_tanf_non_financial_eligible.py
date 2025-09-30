from policyengine_us.model_api import *


class tx_tanf_non_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets non-financial eligibility for Texas Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/part-a-determining-eligibility",
        "https://www.law.cornell.edu/regulations/texas/title-1/part-15/chapter-372/subchapter-B",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        has_eligible_child = spm_unit.any(
            person("tx_tanf_eligible_child", period)
        )

        all_immigration_eligible = spm_unit.all(
            person("tx_tanf_immigration_status_eligible_person", period)
        )

        return has_eligible_child & all_immigration_eligible
