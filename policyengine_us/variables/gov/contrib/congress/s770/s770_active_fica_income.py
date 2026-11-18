from policyengine_us.model_api import *


class s770_active_fica_income(Variable):
    value_type = float
    entity = Person
    label = "FICA covered income included in active entity totals"
    documentation = "Validated FICA covered amount already inside the nonpassive entity total, disjoint from the already-SE subset and draw exclusion. Wages paid separately are not in distributive entity income and must not be subtracted a second time."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
