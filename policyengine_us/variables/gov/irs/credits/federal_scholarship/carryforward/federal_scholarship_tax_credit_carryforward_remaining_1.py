from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.credits.federal_scholarship.carryforward.federal_scholarship_tax_credit_carryforward import (
    _remaining_carryforward,
)


class federal_scholarship_tax_credit_carryforward_remaining_1(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unused Federal Scholarship Tax Credit from 1 prior taxable year(s)"
    unit = USD
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(tax_unit, period, parameters):
        return _remaining_carryforward(tax_unit, period, parameters, 1)
