from openfisca_us.model_api import *


class bi_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income phase-out"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        basic_income = add(tax_unit, period, ["bi_before_phase_out"])
        phase_out = parameters(
            period
        ).contrib.ubi_center.basic_income.phase_out
        agi = tax_unit("adjusted_gross_income", period)
        mars = tax_unit("mars", period)
        threshold = phase_out.threshold[mars]
        income_over_threshold = max_(0, agi - threshold)
        return min_(income_over_threshold * phase_out.rate, basic_income)
