from policyengine_us.model_api import *


class hi_lihrtc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii low income household renters tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        tax_before_credit = taxunit("hi_income_tax_before_credits",period)
        tc_eligible = tax_unit("hi_lihrtc_eligibility", period)
        age_eligible = tax_unit("hi_lihrtc_age_egligibility",period)
        disabled = tax_unit("hi_lihrtc_disabled",period)

        multiple = where(
            disabled,
            1,
            tax_unit("exemptions",period)
        )
        double = tc_eligible & age_eligible

        credit_amount = p.base * where(double,2,1) * multiple
        
        return max(0, tax_before_credit - credit_amount)
