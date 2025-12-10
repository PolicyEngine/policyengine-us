from policyengine_us.model_api import *


class ok_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Oklahoma TANF"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/title-340/chapter-10"
    )
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        # Check for eligible child in the unit
        has_eligible_child = (
            spm_unit.sum(
                spm_unit.members("ok_tanf_eligible_child", period.this_year)
            )
            > 0
        )

        income_eligible = spm_unit("ok_tanf_income_eligible", period)
        resource_eligible = spm_unit("ok_tanf_resource_eligible", period)

        return has_eligible_child & income_eligible & resource_eligible
