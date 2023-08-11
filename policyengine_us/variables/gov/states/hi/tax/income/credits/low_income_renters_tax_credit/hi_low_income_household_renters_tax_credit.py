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

        tax_before_credit = taxunit("hi_income_tax_before_credits",period)
        tc_eligible = tax_unit("hi_lihrtc_eligible", period)
        disabled = tax_unit("is_disabled",period)
        age_eligible = person("age",period) >= p.agi_threshold

        multiple = where(
            disabled,
            1,
            tax_unit("exemptions",period)
        )

        credit_amount = p.base * where(age_eligible,2,1) * multiple
        eligible_credit_amount = credit_amount * where (tc_eligible,1,0)
        
        return max(0, tax_before_credit - eligible_credit_amount)
