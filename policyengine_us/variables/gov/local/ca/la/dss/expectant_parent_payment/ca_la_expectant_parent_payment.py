from policyengine_us.model_api import *


class ca_la_expectant_parent_payment(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Los Angeles County expectant parent payment"
    defined_for = "ca_la_expectant_parent_payment_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.la.dss.expectant_parent_payment
        months_pregnant = person("months_pregnant", period)
        eligible_pregancy_months = max_(0, months_pregnant - 6)
        return p.amount * min_(
            eligible_pregancy_months, p.eligible_pregnancy_months
        )
