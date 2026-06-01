from policyengine_us.model_api import *


class fsla_overtime_premium(Variable):
    value_type = float
    entity = Person
    label = "FLSA overtime premium income"
    documentation = (
        "Annual premium portion of FLSA-qualified overtime compensation included "
        "in employment_income. This is the additional pay above straight-time "
        "compensation, such as the extra 0.5x pay in time-and-a-half overtime. "
        "Datasets should provide source or imputed values when available."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/29/207"
