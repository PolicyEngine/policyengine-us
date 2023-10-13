from policyengine_us.model_api import *


class ca_child_care_payment_standard(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care Payment Standard"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.child_care.rate_ceilings.standard
        provider = person("ca_child_care_provider_category", period)
        time = person("ca_child_care_time_category", period)
        service = person("ca_child_care_service_category", period)
        child = person("is_child", period)
        age = person("age", period)

        return (
            select(
                [age < 2, (age >= 2) & (age <= 5), age > 5],
                [
                    p.under_2[provider][time][service],
                    p.between_2_and_5[provider][time][service],
                    p.over_5[provider][time][service],
                ],
            )
            * child
        )
