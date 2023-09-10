from policyengine_us.model_api import *


class mt_elderly_renter_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Montana Elderly Homeowner/Renter Credit Eligibility"
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_renter.threshold
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        age_eligible = age_head | age_spouse >= p.age
        gross_household_income = tax_unit("mt_gross_household_income", period)
        return age_eligible & (
            gross_household_income < p.income
        )
