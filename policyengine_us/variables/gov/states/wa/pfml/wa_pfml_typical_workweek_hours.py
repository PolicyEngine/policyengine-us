from policyengine_us.model_api import *


class wa_pfml_typical_workweek_hours(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML typical workweek hours"
    documentation = (
        "Optional typical workweek hours for Washington PFML claim "
        "proration. Used only when leave hours claimed are provided."
    )
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.WA
    default_value = 0
    reference = "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010"
