from policyengine_us.model_api import *


class md_hundred_year_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland hundred year subtraction"
    unit = USD
    definition_period = YEAR
    reference = "https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/"
    defined_for = "md_hundred_year_subtraction_eligible"

    adds = ["md_hundred_year_subtraction_person"]
