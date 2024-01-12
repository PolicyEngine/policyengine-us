from policyengine_us.model_api import *


class la_federal_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana federal tax deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",  # 2022 line 8B-line 8C
        "https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=3",  # 2021 line 8A-line 8C
        "https://www.legis.la.gov/Legis/Law.aspx?d=101760",  # (3)
    ]
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        tax_before_refundable_credits = tax_unit(
            "income_tax_before_refundable_credits", period
        )
        investment_tax = tax_unit("net_investment_income_tax", period)
        fed_tax = tax_before_refundable_credits + investment_tax
        lump_sum_distributions = tax_unit(
            "form_4972_lumpsum_distributions", period
        )
        premium_tax_credit = tax_unit("premium_tax_credit", period)
        reductions = lump_sum_distributions + premium_tax_credit
        # The deduction was discontinued in 2022
        p = parameters(period).gov.states.la.tax.income.deductions.federal_tax
        return max_(0, fed_tax - reductions) * p.availability
