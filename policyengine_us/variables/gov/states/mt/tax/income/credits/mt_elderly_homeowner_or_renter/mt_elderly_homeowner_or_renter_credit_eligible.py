from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Montana Elderly Homeowner/Renter Credit"
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        # If the filer is married and both spouses owned or rent the residence
        # Only one of them must meet the age requierments
        # reference: https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=47
        greater_age_head_spouse = person.tax_unit(
            "greater_age_head_spouse", period
        )
        return greater_age_head_spouse >= p.age_threshold
