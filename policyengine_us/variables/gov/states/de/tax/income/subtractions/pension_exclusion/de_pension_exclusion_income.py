from policyengine_us.model_api import *


class de_pension_exclusion_income(Variable):
    value_type = float
    entity = Person
    label = "Income sources for the Delaware pension exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = "gov.states.de.tax.income.subtractions.exclusions.pension.income_sources"
