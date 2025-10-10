from policyengine_us.model_api import *


class tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = (
        "Temporary Assistance for Needy Families (TANF) gross unearned income"
    )
    unit = USD
    definition_period = MONTH

    adds = "gov.hhs.tanf.cash.income.sources.unearned"
