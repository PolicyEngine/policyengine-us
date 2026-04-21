from policyengine_us.model_api import *


class mo_st_louis_earnings_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "St. Louis earnings tax credit"
    documentation = (
        "Optional credit against St. Louis earnings tax, such as for taxes "
        "paid to another state or political subdivision."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
