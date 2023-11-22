from policyengine_us.model_api import *


class mt_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Montana Child Tax Credit"
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.ctc.income_limit
        agi = tax_unit("adjusted_gross_income", period)
        income_eligible = agi <= p.agi
        # CTC limited to filers with investment income below a certain threshold
        investment_income_eligible = (
            tax_unit("earned_income_disqualified_income", period)
            < p.investment
        )

        earned_income = tax_unit("tax_unit_earned_income", period)
        earned_income_eligible = earned_income > 0

        return (
            income_eligible
            & investment_income_eligible
            & earned_income_eligible
        )
