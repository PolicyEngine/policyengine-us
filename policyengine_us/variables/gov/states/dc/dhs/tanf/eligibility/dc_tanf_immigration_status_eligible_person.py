from policyengine_us.model_api import *


class dc_tanf_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for DC Temporary Assistance for Needy Families (TANF) based on immigration status"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.24#(a)"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        return qualified_noncitizen | is_citizen
