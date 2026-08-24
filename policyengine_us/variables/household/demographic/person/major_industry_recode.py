from policyengine_us.model_api import *


class major_industry_recode(Variable):
    value_type = int
    entity = Person
    label = "CPS major industry recode of previous year"
    documentation = (
        "This variable is the WEMIND variable in the Current Population Survey."
    )
    definition_period = YEAR
