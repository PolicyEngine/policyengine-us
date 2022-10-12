from policyengine_us.model_api import *


class domestic_production_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Domestic production activities ALD"
    unit = USD
    documentation = "Above-the-line deduction from gross income for domestic production activities."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199"
