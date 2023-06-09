from policyengine_us.model_api import *


class de_blind_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware blind additional standard deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.deductions

        blind_head = tax_unit("blind_head", period)
        head_eligible = (blind_head).astype(int)

        blind_spouse = tax_unit("blind_spouse", period)
        spouse_eligible = (blind_spouse).astype(int)

        return (head_eligible + spouse_eligible) * p.blind
