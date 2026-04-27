from policyengine_us.model_api import *


class wa_pfml(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML maximum annual benefit"
    documentation = (
        "Maximum annual Washington Paid Family and Medical Leave benefit for "
        "the selected leave type. Computed as the weekly benefit amount "
        "multiplied by the maximum eligible leave duration."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "wa_pfml_eligible"
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010",
    )

    def formula(person, period, parameters):
        weekly_benefit = person("wa_pfml_weekly_benefit_amount", period)
        max_leave_weeks = person("wa_pfml_max_leave_weeks", period)
        return weekly_benefit * max_leave_weeks
