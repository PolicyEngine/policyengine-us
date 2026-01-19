from policyengine_us.model_api import *


class ia_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = YEAR
    defined_for = "ia_tanf_eligible"
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ia_tanf_payment_standard", period)
        countable_income = spm_unit("ia_tanf_countable_income", period)
        return max_(payment_standard - countable_income, 0)
