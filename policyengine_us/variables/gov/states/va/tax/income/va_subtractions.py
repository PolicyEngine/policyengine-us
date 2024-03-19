from policyengine_us.model_api import *


class va_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia subtractions from the adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    adds = "gov.states.va.tax.income.subtractions.subtractions"
