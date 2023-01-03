from policyengine_us.model_api import *


class non_sch_d_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Capital gains not reported on Schedule D"
    unit = USD
    definition_period = YEAR
