from policyengine_us.model_api import *


class mn_mfip_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP"
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        demographic = spm_unit("is_demographic_tanf_eligible", period)
        income = spm_unit("mn_mfip_income_eligible", period)
        resources = spm_unit("mn_mfip_resource_eligible", period)
        return demographic & income & resources
