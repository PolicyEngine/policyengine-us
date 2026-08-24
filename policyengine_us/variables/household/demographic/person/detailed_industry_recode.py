from policyengine_us.model_api import *


class detailed_industry_recode(Variable):
    value_type = int
    entity = Person
    label = "CPS detailed industry recode of previous year"
    documentation = (
        "This variable is the WEIND variable in the Current Population Survey."
    )
    definition_period = YEAR
