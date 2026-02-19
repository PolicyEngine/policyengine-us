from policyengine_us.model_api import *


class nj_unemployment_insurance_base_period_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance base period wages"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-43/section-43-21-4/"
    )
    defined_for = StateCode.NJ
