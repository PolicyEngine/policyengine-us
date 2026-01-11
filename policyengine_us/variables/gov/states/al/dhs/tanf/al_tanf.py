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
        p = parameters(period).gov.states.al.dhs.tanf
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.max_unit_size)
        payment_standard = p.payment_standard.calc(capped_unit_size)
        countable_income = spm_unit("al_tanf_countable_income", period)

        return max_(payment_standard - countable_income, 0)
