from policyengine_us.model_api import *


class head_start_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Head Start gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ecfr.gov/current/title-45/section-1305.2"
    adds = "gov.hhs.head_start.income.sources"
