## md_s_corp_tax_credit_addition.py
from openfisca_us.model_api import *

class md_s_corp_tax_credit_addition(Variable):
    # d. S corporation taxes included on lines 13 and 14 of Form 502CR, Part A, Tax Credits for Income Taxes Paid to Other States and Localities. (See instructions for Part A of Form 502CR.)
    value_type = float
    entity = TaxUnit
    label = "MD S Corporation Tax Credit"
    documentation = "S corporation taxes included on lines 13 and 14 of Form 502CR, Part A, Tax Credits for Income Taxes Paid to Other States and Localities. (See instructions for Part A of Form 502CR.)"
    unit = USD
    definition_period = YEAR