from policyengine_us.model_api import *


class de_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Delaware State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415008PHI"

    def formula(person, period, parameters):
        is_ssi_eligible = person("is_ssi_eligible", period.this_year)
        age = person("age", period.this_year)
        p = parameters(period).gov.states.de.dhss.ssp
        age_eligible = age >= p.age_threshold
        living_arrangement = person.household("de_ssp_living_arrangement", period)
        in_residential_care = (
            living_arrangement == living_arrangement.possible_values.RESIDENTIAL_CARE
        )
        return is_ssi_eligible & age_eligible & in_residential_care
