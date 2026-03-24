from policyengine_us.model_api import *


class pa_philadelphia_wage_tax_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Philadelphia wage tax taxable wages"
    documentation = (
        "Compensation subject to Philadelphia's wage tax or employee earnings "
        "tax for this person."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
