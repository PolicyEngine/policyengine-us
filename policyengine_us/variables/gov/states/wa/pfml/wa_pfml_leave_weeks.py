from policyengine_us.model_api import *


class wa_pfml_leave_weeks(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML leave weeks claimed"
    definition_period = YEAR
    defined_for = StateCode.WA
    default_value = 0
    reference = "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020"
