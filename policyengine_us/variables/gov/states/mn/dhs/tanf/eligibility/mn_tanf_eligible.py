from policyengine_us.model_api import *


class mn_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP"
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        has_children = spm_unit("mn_tanf_count_children", period.this_year) > 0
        income_eligible = spm_unit("mn_tanf_income_eligible", period)
        resource_eligible = spm_unit("mn_tanf_resource_eligible", period)

        return has_children & income_eligible & resource_eligible
