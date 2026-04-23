from policyengine_us.model_api import *


class wa_pfml_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Washington PFML eligible"
    documentation = (
        "Eligibility for Washington Paid Family and Medical Leave "
        "benefits. Requires working at least the qualifying hours "
        "threshold in the qualifying period per RCW 50A.15.010. "
        "Annual hours worked is approximated as weekly hours worked "
        "multiplied by the number of weeks in a year."
    )
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.pfml
        annual_hours = person("weekly_hours_worked", period) * WEEKS_IN_YEAR
        return annual_hours >= p.hours_threshold
