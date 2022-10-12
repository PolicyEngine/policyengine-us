from policyengine_us.model_api import *


class tax_unit_ssi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total SSI for the tax unit"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["ssi"])
