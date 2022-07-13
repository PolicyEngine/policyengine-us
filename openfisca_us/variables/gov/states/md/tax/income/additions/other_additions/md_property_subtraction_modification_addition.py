## md_property_subtraction_modification_addition.py
from openfisca_us.model_api import *

class md_property_subtraction_modification_addition(Variable):
    # q. If you sold or exchanged a property for which you claimed a subtraction modification under Senate Bill 367 (Chapter 231, Acts of 2017) or Senate Bill 580/House Bill 600 (Chapter 544 and Chapter 545, Acts of 2012), enter the amount of the difference between your federal adjusted gross income as reportable under the federal Mortgage Forgiveness Debt Relief Act of 2007 and your federal adjusted gross income as claimed in the taxable year.
    value_type = float
    entity = TaxUnit
    label = "MD property subtraction modification"
    documentation = "If you sold or exchanged a property for which you claimed a subtraction modification under Senate Bill 367 (Chapter 231, Acts of 2017) or Senate Bill 580/House Bill 600 (Chapter 544 and Chapter 545, Acts of 2012), enter the amount of the difference between your federal adjusted gross income as reportable under the federal Mortgage Forgiveness Debt Relief Act of 2007 and your federal adjusted gross income as claimed in the taxable year."
    unit = USD
    definition_period = YEAR