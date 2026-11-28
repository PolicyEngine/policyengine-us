from policyengine_us.model_api import *


class railroad_benefits_medicare_premium_withheld(Variable):
    value_type = float
    entity = Person
    label = "Medicare premiums withheld from Railroad Retirement annuities"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Annual Medicare premiums the Railroad Retirement Board withholds from "
        "the annuities reported in railroad_benefits."
    )
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/wf-114_1-2-2024.pdf#page=2"
    )
