from policyengine_us.model_api import *


class al_ui_high_quarter_wages(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI high quarter wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-72/"
    defined_for = StateCode.AL
