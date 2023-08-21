from policyengine_us.model_api import *


class mt_elderly_renter_credit_eligibility(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Elderly Homeowner/Renter Credit Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_renter_credit
        age_head = tax_unit("age_head", period)
        gross_household_income = tax_unit("mt_agi", period)
        return (age_head >= p.age_min) & (
            gross_household_income < p.income_max
        )
