from policyengine_us.model_api import *


class nj_unemployment_insurance_weeks_claimed(Variable):
    value_type = int
    entity = Person
    label = "New Jersey unemployment insurance weeks claimed"
    unit = "week"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-43/section-43-21-3/"
    )
    defined_for = StateCode.NJ
