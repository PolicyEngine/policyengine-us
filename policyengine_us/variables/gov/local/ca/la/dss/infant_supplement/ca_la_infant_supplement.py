from policyengine_us.model_api import *


class ca_la_infant_supplement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Los Angeles County infant supplement"
    defined_for = "ca_la_infant_supplement_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.la.dss.infant_supplement
        is_in_group_home = person("is_in_foster_care_group_home", period)
        return (
            where(is_in_group_home, p.amount.group_home, p.amount.base)
            * MONTHS_IN_YEAR
        )
