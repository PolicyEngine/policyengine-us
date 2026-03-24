from policyengine_us.model_api import *


class pa_philadelphia_wage_tax_reduced_rate_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Philadelphia reduced wage tax rate"
    documentation = (
        "Whether this person qualifies for Philadelphia's reduced 1.5% "
        "income-based wage tax rate."
    )
    definition_period = YEAR
    default_value = False
