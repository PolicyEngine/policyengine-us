from policyengine_us.model_api import *


class wa_pfml(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML benefit"
    documentation = (
        "Annual Washington Paid Family and Medical Leave benefit. "
        "Computed as the weekly benefit amount multiplied by the "
        "combined maximum leave duration in weeks, for eligible "
        "workers. Represents the maximum potential annual benefit "
        "if the full allowed combined leave is taken."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "wa_pfml_eligible"
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.pfml
        weekly_benefit = person("wa_pfml_weekly_benefit_amount", period)
        return weekly_benefit * p.duration.combined_max_weeks
