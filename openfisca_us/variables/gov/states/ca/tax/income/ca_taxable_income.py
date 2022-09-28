from openfisca_us.model_api import *


class ca_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
    defined_for = StateCode.CA
