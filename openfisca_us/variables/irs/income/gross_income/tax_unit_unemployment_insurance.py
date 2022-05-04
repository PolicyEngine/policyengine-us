from openfisca_us.model_api import *


class tax_unit_unemployment_insurance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit unemployment insurance"
    unit = USD
    documentation = "Tax unit unemployment insurance."
    definition_period = YEAR

    formula = sum_of_variables("unemployment_insurance")

tc_e02300 = taxcalc_read_only_variable("tc_e02300", tax_unit_unemployment_insurance)