from policyengine_us.model_api import *


class personal_exemption_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        aged_blind_count = tax_unit("blind_head", period) + (age_head > 64)

        return aged_blind_count * p.age_blind_multiplier + addition_amount
