from policyengine_us.model_api import *


class al_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama TANF income eligibility"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf#page=2"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf
        countable_income = spm_unit("al_tanf_countable_income", period)
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.max_unit_size)
        payment_standard = p.payment_standard.calc(capped_unit_size)

        return countable_income <= payment_standard
