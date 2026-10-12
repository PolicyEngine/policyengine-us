from policyengine_us.model_api import *


class ky_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kentucky CCAP"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=4"

    def formula(spm_unit, period, parameters):
        # 922 KAR 2:160 Section 3-9: a family must have an eligible child, meet an
        # activity/need pathway, and pass the income test. 922 KAR 2:160 has no
        # asset or resource test, so none is applied.
        has_eligible_child = add(spm_unit, period, ["ky_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("ky_ccap_income_eligible", period)
        activity_eligible = spm_unit("ky_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & activity_eligible
