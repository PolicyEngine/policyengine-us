from policyengine_us.model_api import *


class ok_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma State Supplemental Payment non-income eligibility"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
    defined_for = StateCode.OK

    def formula(person, period, parameters):
        arrangement = person("ssi_federal_living_arrangement", period)
        in_facility = person("ssi_lives_in_medical_treatment_facility", period) | (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        # NOTE: OAC 340:15-1-5(d) bars a person whose needs are in a TANF
        # case, and (c)(4)-(5) change the spouse income test when the spouse
        # or children are in one. Neither is modeled, to avoid a TANF/SSP cycle.
        return (
            person("is_ssi_eligible", period)
            & ~in_facility
            & ~person("is_incarcerated", period)
            & ~person("ok_ssp_is_excluded", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
