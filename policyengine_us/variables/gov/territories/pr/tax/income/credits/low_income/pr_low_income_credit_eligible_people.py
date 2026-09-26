from policyengine_us.model_api import *


class pr_low_income_credit_eligible_people(Variable):
    value_type = int
    entity = TaxUnit
    label = "Eligible people for the Puerto Rico low income credit"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1007/subchapter-b/30212/"
    defined_for = StateCode.PR

    adds = ["pr_low_income_credit_eligible_person"]
