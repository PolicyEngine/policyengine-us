from policyengine_us.model_api import *


class wa_pfml_leave_hours_claimed(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML leave hours claimed"
    documentation = (
        "Optional claimed leave hours for Washington PFML. If positive and "
        "paired with typical workweek hours, this takes precedence over "
        "leave weeks for annual benefit calculations."
    )
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.WA
    default_value = 0
    reference = "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020"
