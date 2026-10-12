from policyengine_us.model_api import *


class is_wccc_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Currently enrolled in Washington Working Connections Child Care"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005"
