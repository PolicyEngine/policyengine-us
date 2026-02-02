from policyengine_us.model_api import *


class tx_harris_rides_subsidy(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Harris County RIDES transportation subsidy"
    reference = "https://rides.harriscountytx.gov/"
    unit = USD
    defined_for = "tx_harris_rides_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.tx.harris.rides

        # Get estimated transportation costs
        # In a real implementation, this would be based on actual trip data
        # For now, we'll use a simplified estimate
        transportation_costs = person(
            "pre_subsidy_transportation_expense", period
        )

        # RIDES subsidizes 60% of trip costs (customer pays 40%)
        subsidy_rate = 1 - p.customer_payment_rate

        return transportation_costs * subsidy_rate
