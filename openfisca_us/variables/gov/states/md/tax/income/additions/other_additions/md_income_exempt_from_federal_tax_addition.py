## md_income_exempt_from_federal_tax_addition.py
from openfisca_us.model_api import *

class md_income_exempt_from_federal_tax_addition(Variable):
    # g. Income exempt from federal tax by federal law or treaty that is not exempt from Maryland tax.
    value_type = float
    entity = TaxUnit
    label = "MD Income Exempt From Federal Tax"
    documentation = "Income exempt from federal tax by federal law or treaty that is not exempt from Maryland tax"
    unit = USD
    definition_period = YEAR