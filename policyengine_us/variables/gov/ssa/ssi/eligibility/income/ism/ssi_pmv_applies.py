from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ssi_pmv_applies(Variable):
    value_type = bool
    entity = Person
    label = "SSI presumed maximum value rule applies"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
        "https://www.law.cornell.edu/cfr/text/20/416.1141",
    )

    def formula(person, period, parameters):
        arrangement = person("ssi_federal_living_arrangement", period)
        is_own_household = arrangement == SSIFederalLivingArrangement.OWN_HOUSEHOLD
        receives_shelter = person(
            "ssi_receives_outside_shelter_support", period
        ) | person("ssi_receives_shelter_from_others_in_household", period)
        # Before 9/30/2024, food also counted as ISM under the PMV rule.
        # After 9/30/2024, only shelter triggers PMV (89 FR 21210).
        food_counts = parameters(period).gov.ssa.ssi.income.ism.food_counts
        receives_food = person("ssi_receives_food_from_others", period)
        receives_ism_support = receives_shelter | (receives_food & food_counts)
        return is_own_household & receives_ism_support
