from policyengine_us.model_api import *


class fl_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TANF eligible"
    definition_period = MONTH
    reference = "Florida Statute § 414.095"
    documentation = "Eligible for Florida Temporary Cash Assistance based on categorical, income, and resource requirements"

    def formula(spm_unit, period, parameters):
        categorically_eligible = spm_unit(
            "fl_tanf_categorically_eligible", period
        )
        income_eligible = spm_unit("fl_tanf_income_eligible", period)
        resource_eligible = spm_unit("fl_tanf_resource_eligible", period)

        return categorically_eligible & income_eligible & resource_eligible
