from policyengine_us.model_api import *


class tn_ccap_part_time(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the child receives part-time care under Tennessee CCAP"
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=48"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.time
        hours = person("childcare_hours_per_week", period.this_year)
        # Full-time care is 20 or more hours per week; part-time is fewer.
        return hours < p.full_time_threshold
