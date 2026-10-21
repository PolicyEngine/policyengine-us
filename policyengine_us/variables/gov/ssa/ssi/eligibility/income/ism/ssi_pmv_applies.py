from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ssi_pmv_applies(Variable):
    value_type = bool
    entity = Person
    label = "SSI presumed maximum value rule applies"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
        "https://www.law.cornell.edu/cfr/text/20/416.1141",
        "https://www.govinfo.gov/content/pkg/FR-2024-03-27/pdf/2024-06464.pdf#page=1",
    )

    def formula(person, period, parameters):
        arrangement = person("ssi_federal_living_arrangement", period)
        is_own_household = arrangement == SSIFederalLivingArrangement.OWN_HOUSEHOLD
        receives_shelter = person(
            "ssi_receives_outside_shelter_support", period
        ) | person("ssi_receives_shelter_from_others_in_household", period)
        # Food stopped counting as ISM on September 30, 2024 (89 FR 21199).
        # Food still counts in a month that starts before that date, except
        # when all of the month's food from others was received or paid for
        # on or after it. The PMV is not prorated by day.
        p = parameters(period).gov.ssa.ssi.income.ism
        food_counts_at_month_end = parameters(period.stop).gov.ssa.ssi.income.ism
        exclusion_starts_this_month = (
            p.food_counts & ~food_counts_at_month_end.food_counts
        )
        food_only_after_exclusion = person(
            "ssi_food_from_others_only_on_or_after_food_exclusion", period
        )
        receives_food = person("ssi_receives_food_from_others", period)
        receives_counted_food = (
            receives_food
            & p.food_counts
            & ~(exclusion_starts_this_month & food_only_after_exclusion)
        )
        return is_own_household & (receives_shelter | receives_counted_food)
