from policyengine_us.model_api import *


class nj_unemployment_insurance_weeks_claimed(Variable):
    value_type = int
    entity = Person
    label = "New Jersey unemployment insurance weeks claimed"
    unit = "week"
    documentation = "Number of weeks for which New Jersey unemployment insurance benefits are claimed. Cannot exceed the maximum benefit weeks (26) or the number of base period weeks worked."
    definition_period = YEAR
    defined_for = StateCode.NJ
