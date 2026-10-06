from policyengine_us.model_api import *


class ma_excess_business_loss_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA excess business loss adjustment"
    documentation = (
        "Massachusetts Schedule X, line 6: the federal excess business loss "
        "(Form 1040, Schedule 1, line 8p), added back to 5.0% income."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2022/dor-2022-inc_form-1_instructions.pdf#page=20",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2024/dor-2024-inc-form-1-inst_1.pdf#page=20",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.excess_business_loss
        return p.in_effect * tax_unit("excess_business_loss", period)
