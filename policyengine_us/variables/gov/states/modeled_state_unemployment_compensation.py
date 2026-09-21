from policyengine_us.model_api import *


class modeled_state_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "modeled state unemployment compensation"
    unit = USD
    documentation = (
        "Unemployment compensation computed from the modeled state "
        "unemployment insurance programs."
    )
    definition_period = YEAR
    adds = [
        "al_ui",
        "nj_unemployment_insurance",
        "ny_ui",
        "ok_ui",
        "pa_uc",
        "ut_ui",
    ]
