from policyengine_us.model_api import *


class mo_capital_gains_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri capital gains subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/faq/taxation/individual/capital-gains-subtraction.html",  # MO form MO-A
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        net_capital_gain = max_(0, tax_unit("net_capital_gain", period))
        p = parameters(
            period
        ).gov.states.mo.tax.income.subtractions.net_capital_gain
        return net_capital_gain * p.rate
