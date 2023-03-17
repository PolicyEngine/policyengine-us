from policyengine_us.model_api import *


class nj_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"
    defined_for = StateCode.NJ

    adds = ["adjusted_gross_income", "nj_agi_additions"]
    subtracts = ["nj_agi_subtractions"]
