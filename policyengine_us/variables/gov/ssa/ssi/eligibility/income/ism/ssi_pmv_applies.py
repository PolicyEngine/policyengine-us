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
        "https://www.law.cornell.edu/cfr/text/20/416.420",
        "https://www.govinfo.gov/content/pkg/FR-2024-03-27/pdf/2024-06464.pdf#page=1",
    )

    def formula(person, period, parameters):
        arrangement = person("ssi_federal_living_arrangement", period)
        is_own_household = arrangement == SSIFederalLivingArrangement.OWN_HOUSEHOLD
        receives_shelter = person(
            "ssi_receives_outside_shelter_support", period
        ) | person("ssi_receives_shelter_from_others_in_household", period)
        # Under 20 CFR 416.420(a), SSA budgets the second prior income
        # month. food_counts dates that income month (89 FR 21199).
        # Food received only on or after September 30, 2024 is excluded;
        # otherwise SSA applies the monthly PMV without daily proration.
        income_period = period.offset(-2, "month")
        # Read this one parameter at each date. parameters(date) builds the
        # whole parameter tree for a date no other formula has asked for,
        # and the income month's last day is such a date every month.
        p_food_counts = parameters.gov.ssa.ssi.income.ism.food_counts
        food_counts = bool(p_food_counts(income_period.start))
        food_counts_at_month_end = bool(p_food_counts(income_period.stop))
        exclusion_starts_this_month = food_counts and not food_counts_at_month_end
        # Use the income month's food receipt when that month falls in
        # the payment year. One-year households lack prior-year inputs.
        support_period = (
            income_period if income_period.start.year == period.start.year else period
        )
        receives_food = person("ssi_receives_food_from_others", support_period)
        receives_counted_food = receives_food & food_counts
        # Read the day-specific flag only in the transition month, so
        # earlier payments do not cache inputs before the model starts.
        if exclusion_starts_this_month:
            food_only_after_exclusion = person(
                "ssi_food_from_others_only_on_or_after_food_exclusion", income_period
            )
            receives_counted_food = receives_counted_food & ~food_only_after_exclusion
        return is_own_household & (receives_shelter | receives_counted_food)
