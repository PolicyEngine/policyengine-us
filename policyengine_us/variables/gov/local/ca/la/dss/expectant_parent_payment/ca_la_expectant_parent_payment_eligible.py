from policyengine_us.model_api import *


class ca_la_expectant_parent_payment_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible for the Los Angeles County expectant parent payment"
    defined_for = "in_la"

    def formula(person, period, parameters):
        foster_care = person("is_in_foster_care", period)
        pregnancy_month = person("current_pregnancy_month", period)
        p = parameters(period).gov.local.ca.la.dss.expectant_parent_payment
        eligible_based_on_pregnancy_month = (
            p.pregnancy_month.min <= pregnancy_month <= p.pregnancy_month.max
        )
        return foster_care & eligible_based_on_pregnancy_month
