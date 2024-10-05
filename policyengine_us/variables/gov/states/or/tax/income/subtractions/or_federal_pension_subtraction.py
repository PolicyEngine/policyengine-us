from policyengine_us.model_api import *


class or_federal_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon Federal Pension Subtraction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2022.pdf#page=84"
    defined_for = StateCode.OR
