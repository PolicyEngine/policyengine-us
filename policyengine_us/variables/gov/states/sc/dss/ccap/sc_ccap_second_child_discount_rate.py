from policyengine_us.model_api import *


class sc_ccap_second_child_discount_rate(Variable):
    value_type = float
    entity = Person
    unit = "/1"
    label = "South Carolina CCAP provider-determined second child discount rate"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=137"
