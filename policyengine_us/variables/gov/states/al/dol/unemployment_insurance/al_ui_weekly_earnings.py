from policyengine_us.model_api import *


class al_ui_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI gross weekly earnings during a partial unemployment week"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-73/",
        "https://oui.doleta.gov/unemploy/pdf/uilawcompar/2023/monetary.pdf#page=20",
    )
    defined_for = StateCode.AL
