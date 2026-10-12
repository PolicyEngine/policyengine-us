from policyengine_us.model_api import *


class ga_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download#page=15",
        "https://www.zillionforms.com/2021/I2122607361.PDF#page14",
    )
    defined_for = StateCode.GA
    adds = ["adjusted_gross_income", "ga_additions"]
    subtracts = ["ga_subtractions"]
