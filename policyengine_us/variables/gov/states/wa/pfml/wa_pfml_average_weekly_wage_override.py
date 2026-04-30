from policyengine_us.model_api import *


class wa_pfml_average_weekly_wage_override(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML average weekly wage override"
    documentation = (
        "Optional override for Washington PFML average weekly wage. Set to a "
        "non-negative dollar amount to replace the annual-income proxy."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    default_value = -1
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
    )
