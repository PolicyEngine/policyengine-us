from policyengine_us.model_api import *


class ks_total_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas total EITC amount (both nonrefundable and refundable)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.credits
        return p.eitc_fraction * tax_unit("earned_income_tax_credit", period)
