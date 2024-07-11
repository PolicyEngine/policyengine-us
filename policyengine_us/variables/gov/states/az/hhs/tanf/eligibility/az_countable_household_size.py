from policyengine_us.model_api import *


class az_countable_household_size(Variable):
    value_type = int
    entity = Household
    label = "Household size"
    definition_period = YEAR

    def formula(household, period, parameters):
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        return min_(household.nb_persons(), p.max_household_size)
