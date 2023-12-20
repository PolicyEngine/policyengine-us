from policyengine_us.model_api import *


class ma_short_term_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts short term capital gains"
    unit = USD
    definition_period = YEAR
    reference = "https://malegislature.gov/Bills/193/H4104/BillHistory"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.capital_gains

        short_term_capital_gains = add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        return p.short_term_capital_gains_rate * short_term_capital_gains
