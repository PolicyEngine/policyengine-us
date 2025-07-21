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
        p = parameters(period).gov.states.dc.dhs
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        qualified_noncitizen = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_statuses,
        )
        return qualified_noncitizen | is_citizen
