from policyengine_us.model_api import *


class de_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Delaware gross income for each individual"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = "gov.states.de.tax.income.gross_income_sources"
