from policyengine_us.model_api import *


class ks_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas nonrefundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income
        nonrefundable_credits = (
            p.credits.nonrefundable_before_eitc
            + ["ks_nonrefundable_eitc"]
            + p.credits.nonrefundable_after_eitc
        )
        return add(tax_unit, period, nonrefundable_credits)
