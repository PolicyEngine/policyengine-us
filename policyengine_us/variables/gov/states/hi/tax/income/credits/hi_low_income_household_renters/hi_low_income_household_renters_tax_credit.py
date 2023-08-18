from policyengine_us.model_api import *


class hi_low_income_household_renters_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii low income household renters tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        tax_before_credit = tax_unit("hi_income_tax_before_credits", period)
        # Aged extra exemptions
        aged_head = (
            tax_unit("age_head", period) >= p.threshold.age
        ).astype(int)
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.threshold.age
        ).astype(int)

        aged_exemptions = aged_head + aged_spouse
        exemptions = tax_unit("exemptions", period)

        total_exemptions = exemptions + aged_exemptions
        credit_amount = p.base * total_exemptions
        return min_(credit_amount, tax_before_credit)
