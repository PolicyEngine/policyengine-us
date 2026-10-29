from policyengine_us.model_api import *


class railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement Board benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Gross annual benefits paid by the Railroad Retirement Board, such as "
        "retirement, disability, spouse and survivor annuities, before Medicare "
        "premiums or other amounts are withheld."
    )
    default_value = 0
