from policyengine_us.model_api import *


class medicaid_ltss_medically_needy_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS medically needy expenses"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit monthly exclusions, post-eligibility deductions, and "
        "incurred medical expenses used to derive Washington remaining or "
        "net available income. This trusted input must already reflect the "
        "applicable expense categories, ordering, and documentation; the "
        "model does not adjudicate expenses or calculate a spenddown budget "
        "period."
    )
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1395",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-515-1508",
    )
