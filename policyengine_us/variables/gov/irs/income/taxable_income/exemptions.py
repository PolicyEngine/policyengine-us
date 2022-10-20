from policyengine_us.model_api import *


class exemptions(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of tax exemptions"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["tax_unit_size"])
