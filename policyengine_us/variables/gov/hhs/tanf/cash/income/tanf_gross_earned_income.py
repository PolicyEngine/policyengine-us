from policyengine_us.model_api import *


class tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = (
        "Temporary Assistance for Needy Families (TANF) gross earned income"
    )
    unit = USD
    definition_period = MONTH

    adds = "gov.hhs.tanf.cash.income.sources.earned"
