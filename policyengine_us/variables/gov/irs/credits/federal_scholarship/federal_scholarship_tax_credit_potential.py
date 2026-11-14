from policyengine_us.model_api import *


class federal_scholarship_tax_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Current-year Federal Scholarship Tax Credit potential"
    unit = USD
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"
    adds = ["federal_scholarship_tax_credit_person"]
