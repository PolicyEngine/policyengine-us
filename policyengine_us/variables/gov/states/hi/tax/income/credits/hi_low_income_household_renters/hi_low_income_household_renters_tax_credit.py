from policyengine_us.model_api import *


class hi_tax_credit_for_low_income_household_renters(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii low income household renters tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "hi_tax_credit_for_low_income_household_renters_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        # Aged extra exemptions
        aged_head = (
            tax_unit("age_head", period) >= p.aged_age_threshold
        ).astype(int)
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.aged_age_threshold
        ).astype(int)

        aged_exemptions = aged_head + aged_spouse
        exemptions = tax_unit("exemptions_count", period)

        total_exemptions = exemptions + aged_exemptions
        return p.amount * total_exemptions
