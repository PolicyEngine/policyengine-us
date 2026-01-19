from policyengine_us.model_api import *


class ia_tanf_payment_standard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF payment standard eligible (Test 3)"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("ia_tanf_countable_income", period)
        payment_standard = spm_unit("ia_tanf_payment_standard", period)
        return countable_income < payment_standard
