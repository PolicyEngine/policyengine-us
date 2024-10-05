from policyengine_us.model_api import *


class ks_nonrefundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas EITC nonrefundable amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        total_eitc = tax_unit("ks_total_eitc", period)
        pre_credit_tax = tax_unit("ks_income_tax_before_credits", period)
        p = parameters(period).gov.states.ks.tax.income
        pre_eitc_credits = p.credits.nonrefundable_before_eitc
        credits_before_eitc = add(tax_unit, period, pre_eitc_credits)
        tax_before_eitc = max_(0, pre_credit_tax - credits_before_eitc)
        diff = total_eitc - tax_before_eitc
        return where(diff <= 0, total_eitc, tax_before_eitc)
