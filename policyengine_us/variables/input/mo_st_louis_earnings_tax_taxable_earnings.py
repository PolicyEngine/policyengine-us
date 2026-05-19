from policyengine_us.model_api import *


class mo_st_louis_earnings_tax_taxable_earnings(Variable):
    value_type = float
    entity = Person
    label = "St. Louis earnings tax taxable earnings"
    documentation = (
        "Earnings subject to the City of St. Louis earnings tax for this person."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
