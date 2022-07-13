## md_taxable_tax_preference_items_addition.py
from openfisca_us.model_api import *

class md_taxable_tax_preference_items_addition(Variable):
    # i. Taxable tax preference items from line 5 of Form 502TP. The items of tax preference are defined in IRC Section 57. If the total of your tax preference items is more than $10,000 ($20,000 for married taxpayers filing joint returns) you must complete and attach Form 502TP, whether or not you are required to file federal Form 6251 (Alternative Minimum Tax) with your federal Form 1040.
    value_type = float
    entity = TaxUnit
    label = "MD Taxable Tax Preference Items"
    documentation = "Taxable tax preference items from line 5 of Form 502TP. The items of tax preference are defined in IRC Section 57. If the total of your tax preference items is more than $10,000 ($20,000 for married taxpayers filing joint returns) you must complete and attach Form 502TP, whether or not you are required to file federal Form 6251 (Alternative Minimum Tax) with your federal Form 1040."
    unit = USD
    definition_period = YEAR