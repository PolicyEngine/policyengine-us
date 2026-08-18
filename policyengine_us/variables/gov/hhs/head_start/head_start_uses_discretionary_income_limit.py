from policyengine_us.model_api import *


class head_start_uses_discretionary_income_limit(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Head Start program uses the discretionary income limit"
    documentation = (
        "Whether the family's Head Start or Early Head Start program applies "
        "the 45 CFR 1302.12(d) allowance to enroll families with income "
        "between 100% and 130% of the poverty guidelines. Programs may fill "
        "up to 35% of enrollment this way; set directly when the local "
        "program does so."
    )
    definition_period = YEAR
    default_value = False
    reference = "https://www.ecfr.gov/current/title-45/section-1302.12#p-1302.12(d)"
