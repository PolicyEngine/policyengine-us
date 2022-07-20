from openfisca_us.model_api import *

class ca_young_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA earned income tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"