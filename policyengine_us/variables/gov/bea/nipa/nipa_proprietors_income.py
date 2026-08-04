from policyengine_us.model_api import *


class nipa_proprietors_income(Variable):
    value_type = float
    entity = Person
    label = "NIPA proprietors' income"
    documentation = (
        "PolicyEngine person-level mapping for BEA NIPA proprietors' "
        "income with inventory valuation and capital consumption "
        "adjustments, Table 2.1 line 9, using the closest additive "
        "microdata concepts."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.bea.gov/itable/national-gdp-and-personal-income"
    adds = [
        "self_employment_income_before_lsr",
        "farm_income",
        "partnership_s_corp_income",
    ]
