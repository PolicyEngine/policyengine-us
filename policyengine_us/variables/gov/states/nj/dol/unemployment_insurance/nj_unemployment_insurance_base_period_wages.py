from policyengine_us.model_api import *


class nj_unemployment_insurance_base_period_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance base period wages"
    unit = USD
    documentation = "Total wages earned during the base period for New Jersey unemployment insurance eligibility determination."
    definition_period = YEAR
    defined_for = StateCode.NJ
