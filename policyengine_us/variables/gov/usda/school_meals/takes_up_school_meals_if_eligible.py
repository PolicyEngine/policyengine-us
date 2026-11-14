from policyengine_us.model_api import *


class takes_up_school_meals_if_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether an eligible SPM unit takes up school meals"
    definition_period = YEAR
    default_value = True
    documentation = (
        "Whether this SPM unit participates in free or reduced-price school "
        "breakfast and lunch when eligible. Applies to all K-12 children in "
        "the unit. Defaults to true to preserve amounts when callers omit "
        "this input."
    )
    reference = "https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6#p-245.6(c)(6)(iii)"
