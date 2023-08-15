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
        ).gov.states.mt.tax.income.credits.ctc.eligibility.income_limit
        # CTC limited to filers with AGI at or below $56,000
        agi = tax_unit("adjusted_gross_income", period)
        income_eligible = agi <= p.agi
        # CTC limited to filers with investment income below $10,300
        investment_income_eligible = (
            tax_unit("net_investment_income", period) < p.investment
        )
        # proof of earned income
        # Add earned_income in test
        earned_income = tax_unit("tax_unit_earned_income", period)
        proof_earned_income = earned_income > p.earned_income_required

        return (
            income_eligible & investment_income_eligible & proof_earned_income
        )
