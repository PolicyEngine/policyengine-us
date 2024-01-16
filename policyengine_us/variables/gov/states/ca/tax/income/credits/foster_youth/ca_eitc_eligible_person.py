from policyengine_us.model_api import *


class ca_eitc_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California foster youth tax credit"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        
        return tax_unit("ca_eitc_eligible",period)