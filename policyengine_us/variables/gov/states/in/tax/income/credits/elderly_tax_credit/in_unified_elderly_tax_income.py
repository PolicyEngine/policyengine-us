from policyengine_us.model_api import *


class in_unified_elderly_tax_income(Variable):
    value_type = float
    entity = Person
    label = "Indiana unified elderly tax credit income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Income that is utilized for the elderly credit calculation"
    )
    reference = "https://forms.in.gov/Download.aspx?id=15394 "
    defined_for = StateCode.IN

    adds = "gov.states.in.tax.income.credits.unified_elderly.income_sources"
