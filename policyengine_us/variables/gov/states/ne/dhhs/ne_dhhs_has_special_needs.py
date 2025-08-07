from policyengine_us.model_api import *


class ne_dhhs_has_special_needs(Variable):
    value_type = bool
    entity = Person
    label = "Has special needs under Nebraska Department of Health and Human Services"
    definition_period = YEAR
    documentation = "A child has a requirement for extra care because of an acute or chronic physical or mental condition"
    reference = (
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=31",
        "https://dhhs.ne.gov/licensure/Documents/CCC391-3.pdf#page=11",
    )

    def formula(person, period, parameters):
        return person("is_disabled", period)
