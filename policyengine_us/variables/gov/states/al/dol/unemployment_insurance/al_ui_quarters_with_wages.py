from policyengine_us.model_api import *


class al_ui_quarters_with_wages(Variable):
    value_type = int
    entity = Person
    label = "Alabama UI quarters with wages"
    definition_period = YEAR
    default_value = 0
    reference = "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-77/"
    defined_for = StateCode.AL
