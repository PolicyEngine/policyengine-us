from policyengine_us.model_api import *


class az_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona standard deduction"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = [
        "az_base_standard_deduction",
        "az_increased_standard_deduction_for_charitable_contributions",
    ]
