from policyengine_us.model_api import *


class de_aged_blind_additional_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "DE aged and blind additional standard deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        aged_blind_count = tax_unit("aged_blind_count", period)
        p = parameters(period).gov.states.de.tax.income.deductions
        return aged_blind_count * p.additional_standard
