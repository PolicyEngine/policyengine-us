from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Montana Elderly Homeowner/Renter Credit Eligibility"
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter_credit.eligibility
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        # If the filer is married and both spouses owned or rent the residence
        # Only one of them must meet the age requierments
        # reference: https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=47
        age_eligible = age_head | age_spouse >= p.age_threshold
        gross_household_income = tax_unit("mt_gross_household_income", period)
        return age_eligible & (gross_household_income < p.income_limit)
