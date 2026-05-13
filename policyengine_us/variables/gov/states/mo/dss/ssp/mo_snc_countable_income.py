from policyengine_us.model_api import *


class mo_snc_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri SNC countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MO
    documentation = (
        "Approximates Supplemental Nursing Care income from modeled cash "
        "income sources; Missouri-specific disregards are not modeled."
    )
    reference = (
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0610-000-00/0610-005-00/",
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0610-000-00/0610-025-00/",
    )
    adds = ["market_income", "social_security", "ssi"]
