from policyengine_us.model_api import *


class dc_gac_countable_unearned_income_person(Variable):
    value_type = float
    entity = Person
    label = (
        "DC General Assistance for Children (GAC) unearned income per person"
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a#(e)"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        unearned_income = person("dc_tanf_gross_unearned_income", period)
        eligible_child = person("dc_gac_eligible_child", period)
        return unearned_income * eligible_child
