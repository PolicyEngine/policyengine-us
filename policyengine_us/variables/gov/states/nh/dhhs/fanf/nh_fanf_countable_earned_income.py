from policyengine_us.model_api import *


class nh_fanf_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire FANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
        "https://www.dhhs.nh.gov/fam_htm/",
    )
    defined_for = StateCode.NH

    def formula(person, period, parameters):
        # NOTE: NH has different disregard rates for applicants (20%) vs
        # recipients (50%). PolicyEngine cannot track prior benefit receipt,
        # so we apply the 50% recipient rate as it is more favorable.
        p = parameters(period).gov.states.nh.dhhs.fanf.income
        gross_earned = person("tanf_gross_earned_income", period)
        return gross_earned * (1 - p.earned_income_disregard_rate)
