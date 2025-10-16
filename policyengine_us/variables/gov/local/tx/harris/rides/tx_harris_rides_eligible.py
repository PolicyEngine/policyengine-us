from policyengine_us.model_api import *


class tx_harris_rides_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Harris County RIDES eligibility"
    reference = "https://rides.harriscountytx.gov/Registration/Registration-Information"
    defined_for = "in_harris_county_tx"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.tx.harris.rides

        # Age eligibility
        age = person("age", period)
        age_eligible = age >= p.age_threshold

        # Disability eligibility
        has_disability = person("is_disabled", period)

        return age_eligible | has_disability
