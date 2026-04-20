from policyengine_us.model_api import *


class al_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama TANF"
    unit = USD
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf#page=2"
    defined_for = "al_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("al_tanf_payment_standard", period)
        countable_income = spm_unit("al_tanf_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
