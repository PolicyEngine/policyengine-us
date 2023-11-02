from policyengine_us.model_api import *


class ga_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://houpl.org/wp-content/uploads/2023/01/2022-IT-511_Individual_Income_Tax_-Booklet-compressed.pdf#page=14",
        "https://www.zillionforms.com/2021/I2122607361.PDF#page14",
    )
    defined_for = StateCode.GA
    adds = ["adjusted_gross_income", "ga_additions"]
    subtracts = ["ga_subtractions"]
