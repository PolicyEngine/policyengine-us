from policyengine_us.model_api import *


class pr_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico adjusted gross income person level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/"
