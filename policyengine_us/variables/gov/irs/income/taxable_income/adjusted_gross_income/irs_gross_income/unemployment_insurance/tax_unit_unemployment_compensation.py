from policyengine_us.model_api import *


class tax_unit_unemployment_compensation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit unemployment compensation"
    unit = USD
    documentation = "Combined unemployment compensation for the tax unit."
    definition_period = YEAR

    formula = sum_of_variables(["unemployment_compensation"])
