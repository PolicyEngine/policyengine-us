from policyengine_us.model_api import *


class wa_pfml_qualifying_period_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML qualifying-period hours worked override"
    documentation = (
        "Optional override for hours worked in the Washington PFML "
        "qualifying period. Set to a non-negative number of hours to replace "
        "the annualized weekly-hours proxy used for eligibility."
    )
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.WA
    default_value = -1
    reference = "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010"
