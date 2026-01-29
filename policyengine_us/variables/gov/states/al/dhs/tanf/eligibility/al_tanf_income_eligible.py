from policyengine_us.model_api import *


class al_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama TANF income eligibility"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf#page=2"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("al_tanf_countable_income", period)
        payment_standard = spm_unit("al_tanf_payment_standard", period)
        return countable_income <= payment_standard
