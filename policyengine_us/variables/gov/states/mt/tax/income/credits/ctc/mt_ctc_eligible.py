from policyengine_us.model_api import *


class mt_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Montana Child Tax Credit"
    definition_period = YEAR
    unit = USD
    reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.ctc
        # CTC limited to filers with agi at or below $56,000
        agi = tax_unit("adjusted_gross_income", period)
        income_eligible = agi <= p.income_threshold
        investment_income_eligible = (
            tax_unit("net_investment_income", period) < p.investment_threshold
        )
        return income_eligible & investment_income_eligible
